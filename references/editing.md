# Edit, Finish & Export (ffmpeg)

Raw Seedance clips are footage, not an ad. This stage assembles them into one
broadcast-grade spot. `scripts/assemble_video.py` wraps the common ffmpeg work; reach
for raw ffmpeg only for anything the script doesn't cover.

## Prereqs
ffmpeg is available in the sandbox (`ffmpeg -version`). Work from **local** clip files
(download via `scripts/fetch_media.py`) — never feed fal CDN URLs to ffmpeg.

## 1. Trim to scripted in/out
Each clip should contribute only its scripted seconds. Trim:
```
ffmpeg -i shot1.mp4 -ss 0 -t 2 -c:v libx264 -c:a aac shot1_trim.mp4
```
Re-encode (not `-c copy`) so all clips share codec/timebase before concat.

## 2. Normalize every clip to one spec
Before concatenating, force a uniform spec — same size, fps, SAR, pixel format —
otherwise concat glitches:
```
-vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30"
-pix_fmt yuv420p
```
(Use 1080x1920 for 9:16, 1080x1080 for 1:1.)

## 3. Assemble
Default to **hard cuts** (concat) — they're the language of modern ads. Use short
crossfades only where motivated.
- Hard cut concat (filter graph, safe across sources):
  `concat=n=N:v=1:a=1`
- Crossfade between two clips: `xfade=transition=fade:duration=0.3:offset=<t>` and
  `acrossfade` for audio.

`scripts/assemble_video.py` does trim + normalize + concat with optional per-cut
crossfades from a `shots.json` manifest.

## 4. Audio
A TV spot has a deliberate mix:
- **Music bed**: lay one track under the whole spot. Duck it ~ -8 to -12 dB under VO.
- **VO / dialogue**: from Seedance lip-sync or a separate VO; keep it forward.
- **Diegetic SFX**: keep useful clip audio (whooshes, clicks); mute clip audio that
  fights the bed.
- **Loudness normalize** at the end:
  - Web/social: ~ **-14 LUFS** → `loudnorm=I=-14:TP=-1.5:LRA=11`
  - Broadcast (EBU R128): **-23 LUFS** → `loudnorm=I=-23:TP=-1:LRA=7`
- End with a clean music "button" (resolved note), not an abrupt cut.

## 5. Titles, logo & end card
Add real text in post (sharper and more legible than baked-in AI text).
- On-screen text from the script via `drawtext` (specify font, size, color, box, fade).
- Logo overlay via `overlay` with a PNG (respect safe margins — keep text/logo within
  ~10% of edges).
- **End card** (~2–3s): product + logo + tagline + CTA. Either overlay text on a
  generated plate, or build a solid/branded card with `drawtext`. This is the frame
  people remember — make it crisp and on-brand.

Example drawtext:
```
drawtext=fontfile=/path/font.ttf:text='Feel the difference':fontcolor=white:fontsize=64:\
x=(w-text_w)/2:y=h*0.8:box=1:boxcolor=black@0.4:boxborderw=20:enable='between(t,1,4)'
```

## 6. Color grade
Apply one consistent look so shots feel like a single film:
- Quick filmic warmth: `eq=contrast=1.06:saturation=1.08`, plus
  `curves=preset=lighter` or a subtle `colorbalance`.
- Or apply a LUT: `lut3d=look.cube`.
Keep it subtle and identical across all shots.

## 7. Export spec
- Container/codec: MP4, H.264 (`libx264`), `-pix_fmt yuv420p` (universal playback).
- Quality: `-crf 18` (high) `-preset slow`; audio `aac -b:a 256k`.
- Frame rate: 24 or 30fps, consistent. Resolution 1080p; locked aspect ratio.
- **Verify final duration ≤ target** (`ffprobe -show_entries format=duration`).
- Optionally export a platform cutdown (e.g. 9:16 for Reels/TikTok) by re-framing.

## 8. Deliver
Present the final MP4 with `present_files` and a one-line summary. Offer a 6s/15s
cutdown, an alternate aspect ratio, or an end-card revision as easy follow-ups.
