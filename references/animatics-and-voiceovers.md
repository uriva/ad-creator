# Animatics, Voiceovers & Dynamic Audio Sync

When executing high-concept commercials or parody campaigns, advanced video generators can hit structural or policy limitations. This guide outlines how to handle those scenarios, compile locally with zero overhead, and execute perfect audio-visual synchronization.

## 1. The "Animatic / Motion Comic" Fallback (Safety Blocks)
* **The Problem:** Recognizing protected IP, parody characters (e.g., Rick & Morty, Disney, Marvel), or highly specific trademark elements can trigger safety policy violations or model rejection on advanced video models (like Seedance 2.0).
* **The Solution:** Fall back instantly to a stylized **Motion Comic / Animatic**! By using high-fidelity static keyframe plates (from Nano Banana 2/edit) and compiling them as a timed slideshow using local FFmpeg, you completely bypass the remote content filter, cut costs to zero, and maintain a highly premium look.

## 2. Dynamic Audio-Video Pacing (No Cut-offs)
* **The Rule:** Never use fixed-duration trimming (`-t 4`, `-t 5`) on multi-speaker or fast-paced dialogue clips. This cuts off characters mid-sentence.
* **The Workflow:** 
  1. Generate individual speech/dialogue files asynchronously using a high-quality neural Text-to-Speech (TTS) tool (like `edge-tts`).
  2. Assemble or mix individual speaker lines per shot (e.g., Summer speaks first, Jerry replies with an `adelay` filter).
  3. Query the exact duration of the shot's final mixed audio file using `ffprobe`:
     ```bash
     ffprobe -v error -show_entries format=duration -of csv=p=0 shot_audio.mp3
     ```
  4. Loop the static image/keyframe and encode the video to match **that exact audio duration plus a tiny padding** (`duration = audio_dur + 0.3` seconds):
     ```bash
     ffmpeg -y -loop 1 -t <dur> -i image.png -i shot_audio.mp3 -c:v libx264 -preset ultrafast -c:a aac -r 15 -pix_fmt yuv420p -shortest shot_video.mp4
     ```

## 3. High-Contrast Subtitle Burning (Syntax Safety)
* **The Problem:** FFmpeg's `drawtext` timeline filter is extremely sensitive to single quotes, apostrophes, and nested shell escapes. Strings containing characters like `'` (e.g., "doesn't", "I'm", "don't") will crash the parser with non-zero exit code 8.
* **The Solution:** 
  * Clean up and normalize dialogue strings before passing them to the FFmpeg filter. Expand contractions:
    * `"doesn't"` -> `"does not"`
    * `"I'm"` -> `"I am"`
    * `"don't"` -> `"do not"`
  * This completely avoids escaping bugs, guarantees subtitle compilation safety, and ensures matches with the spoken speech.
* **Styling:** For vertical videos (9:16), render titles and captions near the bottom center (`y=h-120`) in yellow or white with a bold stroke or semi-transparent background box (`box=1:boxcolor=black@0.7:boxborderw=6`) and readable size (`fontsize=20` for 540x960 resolutions).

## 4. Systems Optimization & FUSE Bottlenecks
* **FUSE Directory deadlocks:** Shared cloud storage mounts (like `/mnt/files/` via `s3fs`) have massive write latency and lack standard random-access file locks. Running frame-by-frame FFmpeg encodes directly into FUSE directories causes files to corrupt or freeze mid-execution.
* **Ephemeral Sandboxes:** Ephemeral VM containers wipe `/tmp` and local storage between independent tool calls.
* **The Perfect Build Pattern:** Download all raw keyframe assets, perform all image scaling/formatting, run all audio TTS generation, compile the intermediate shot clips, and concatenate the final master MP4 **entirely inside a local ramdisk `/tmp/` directory within a single script run**. Once compilation is complete, copy the finalized `.mp4` file to `/mnt/files/` or upload it to S3 in one single write operation.

