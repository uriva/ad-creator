#!/usr/bin/env python3
"""Assemble Seedance clips into a finished commercial with ffmpeg.

Does the deterministic post work: trim each clip to its scripted length, normalize
all clips to one spec (size / fps / SAR / pixel format / audio), concatenate (hard
cuts or crossfades), optionally lay a ducked music bed, loudness-normalize, and
export a broadcast-spec MP4.

Driven by a JSON manifest (see --help example). Titles, logo overlays, and end cards
are best added with bespoke ffmpeg drawtext/overlay (see references/editing.md);
this script handles the structural edit + audio so those overlays compose cleanly.

Usage:
    python assemble_video.py --manifest shots.json --out final.mp4

Manifest schema:
{
  "width": 1920, "height": 1080, "fps": 30,
  "crossfade": 0.0,                 # seconds; 0 = hard cuts
  "music": "assets/bed.mp3",        # optional music bed
  "music_db": -10,                  # bed gain relative to mix (dB), default -10
  "loudness": "web",                # "web" (-14 LUFS) | "broadcast" (-23) | "none"
  "shots": [
    {"file": "assets/shot1.mp4", "in": 0.0, "duration": 2.0, "mute": false},
    {"file": "assets/shot2.mp4", "in": 0.0, "duration": 4.0, "mute": false}
  ]
}

Requires ffmpeg + ffprobe on PATH.
"""
import argparse
import json
import os
import shlex
import subprocess
import sys
import tempfile


def run(cmd):
    print("+ " + " ".join(shlex.quote(c) for c in cmd), file=sys.stderr)
    subprocess.run(cmd, check=True)


def has_audio(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
         "stream=index", "-of", "csv=p=0", path],
        capture_output=True, text=True)
    return bool(out.stdout.strip())


def duration_of(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path], capture_output=True, text=True)
    try:
        return float(out.stdout.strip())
    except ValueError:
        return 0.0


def normalize_clip(src, dst, w, h, fps, t_in, dur, mute):
    """Trim + scale/pad + uniform pixfmt/fps + guaranteed AAC stereo 48k audio."""
    vf = (f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
          f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps},format=yuv420p")
    cmd = ["ffmpeg", "-y", "-ss", str(t_in), "-t", str(dur), "-i", src]
    if mute or not has_audio(src):
        cmd += ["-f", "lavfi", "-t", str(dur), "-i",
                "anullsrc=channel_layout=stereo:sample_rate=48000"]
        amap = "1:a"
    else:
        amap = "0:a"
    cmd += ["-map", "0:v", "-map", amap,
            "-vf", vf, "-r", str(fps),
            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "256k",
            "-shortest", dst]
    run(cmd)


def concat_hardcut(clips, out):
    lst = out + ".txt"
    with open(lst, "w") as f:
        for c in clips:
            f.write(f"file '{os.path.abspath(c)}'\n")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst,
         "-c", "copy", out])
    os.remove(lst)


def concat_crossfade(clips, out, xf, w, h, fps):
    """Chain xfade (video) + acrossfade (audio) across all clips."""
    durs = [duration_of(c) for c in clips]
    inputs = []
    for c in clips:
        inputs += ["-i", c]
    fc = []
    vprev, aprev = "0:v", "0:a"
    offset = durs[0] - xf
    for i in range(1, len(clips)):
        vout = f"v{i}"
        aout = f"a{i}"
        fc.append(f"[{vprev}][{i}:v]xfade=transition=fade:duration={xf}:offset={offset:.3f}[{vout}]")
        fc.append(f"[{aprev}][{i}:a]acrossfade=d={xf}[{aout}]")
        vprev, aprev = vout, aout
        # next offset: running total minus the cumulative crossfades
        offset += durs[i] - xf
    cmd = ["ffmpeg", "-y"] + inputs + [
        "-filter_complex", ";".join(fc),
        "-map", f"[{vprev}]", "-map", f"[{aprev}]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "256k", out]
    run(cmd)


def add_music_and_loudness(video, out, music, music_db, loudness):
    loud_map = {"web": "I=-14:TP=-1.5:LRA=11", "broadcast": "I=-23:TP=-1:LRA=7"}
    af_loud = loud_map.get(loudness)
    if music:
        # Duck nothing fancy: mix clip audio (full) with music bed lowered by music_db.
        fc = (f"[1:a]volume={music_db}dB[bed];"
              f"[0:a][bed]amix=inputs=2:duration=first:dropout_transition=2[mix]")
        amap = "[mix]"
        cmd = ["ffmpeg", "-y", "-i", video, "-stream_loop", "-1", "-i", music,
               "-filter_complex", fc, "-map", "0:v", "-map", amap]
    else:
        cmd = ["ffmpeg", "-y", "-i", video, "-map", "0:v", "-map", "0:a"]
    if af_loud:
        cmd += ["-af", f"loudnorm={af_loud}"]
    cmd += ["-c:v", "copy" if not music and not af_loud else "libx264",
            "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "256k",
            "-movflags", "+faststart", out]
    # if we set -c:v copy together with re-mux only, ensure valid: when copy chosen there's no preset/crf effect
    run(cmd)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out", default="final.mp4")
    ap.add_argument("--workdir", default=None, help="Temp dir for intermediates.")
    args = ap.parse_args()

    with open(args.manifest) as f:
        m = json.load(f)

    w = int(m.get("width", 1920))
    h = int(m.get("height", 1080))
    fps = int(m.get("fps", 30))
    xf = float(m.get("crossfade", 0) or 0)
    music = m.get("music")
    music_db = m.get("music_db", -10)
    loudness = m.get("loudness", "web")
    shots = m["shots"]
    if not shots:
        sys.exit("Manifest has no shots.")

    workdir = args.workdir or tempfile.mkdtemp(prefix="adedit_")
    os.makedirs(workdir, exist_ok=True)

    norm = []
    for i, s in enumerate(shots):
        dst = os.path.join(workdir, f"norm_{i:02d}.mp4")
        dur = float(s.get("duration") or duration_of(s["file"]))
        normalize_clip(s["file"], dst, w, h, fps, float(s.get("in", 0)), dur,
                       bool(s.get("mute", False)))
        norm.append(dst)

    combined = os.path.join(workdir, "combined.mp4")
    if xf > 0 and len(norm) > 1:
        concat_crossfade(norm, combined, xf, w, h, fps)
    else:
        concat_hardcut(norm, combined)

    if music or loudness in ("web", "broadcast"):
        add_music_and_loudness(combined, args.out, music, music_db, loudness)
    else:
        run(["ffmpeg", "-y", "-i", combined, "-c", "copy",
             "-movflags", "+faststart", args.out])

    print(args.out)
    print(f"final duration: {duration_of(args.out):.2f}s", file=sys.stderr)


if __name__ == "__main__":
    main()
