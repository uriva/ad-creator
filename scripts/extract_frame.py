#!/usr/bin/env python3
"""Extract a single frame from a clip as a PNG — for scene continuity.

The main use is the "clip-tail handoff": grab the LAST frame of clip N and feed it as
the starting `image_url` of clip N+1 so two consecutive Seedance shots flow as one
continuous move. Also handy to pull the first frame or a frame at a given time.

Usage:
    python extract_frame.py clipN.mp4 --last  --out lastframe.png      # default
    python extract_frame.py clipN.mp4 --first --out firstframe.png
    python extract_frame.py clipN.mp4 --time 2.5 --out frame_2p5.png

Prints the output path. Requires ffmpeg + ffprobe.
"""
import argparse
import subprocess
import sys


def run(cmd):
    subprocess.run(cmd, check=True, capture_output=True)


def extract_last(src, dst):
    # Seek a hair before EOF and grab one frame. Robust across variable frame rates.
    run(["ffmpeg", "-y", "-sseof", "-0.2", "-i", src,
         "-update", "1", "-frames:v", "1", "-q:v", "2", dst])


def extract_first(src, dst):
    run(["ffmpeg", "-y", "-i", src, "-frames:v", "1", "-q:v", "2", dst])


def extract_at(src, dst, t):
    run(["ffmpeg", "-y", "-ss", str(t), "-i", src,
         "-frames:v", "1", "-q:v", "2", dst])


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clip", help="Input video file.")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--last", action="store_true", help="Last frame (default).")
    g.add_argument("--first", action="store_true", help="First frame.")
    g.add_argument("--time", type=float, help="Frame at this timestamp (seconds).")
    ap.add_argument("--out", default="frame.png", help="Output PNG path.")
    args = ap.parse_args()

    try:
        if args.first:
            extract_first(args.clip, args.out)
        elif args.time is not None:
            extract_at(args.clip, args.out, args.time)
        else:
            extract_last(args.clip, args.out)
    except subprocess.CalledProcessError as e:
        print(f"ffmpeg failed: {e}", file=sys.stderr)
        sys.exit(1)
    print(args.out)


if __name__ == "__main__":
    main()
