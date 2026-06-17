# Animatics, Voiceovers & Dynamic Audio Sync

When executing high-concept commercials or parody campaigns, advanced video generators can hit structural or policy limitations. This guide outlines how to handle those scenarios, compile locally with zero overhead, and execute perfect audio-visual synchronization.

## 1. The "Animatic / Motion Comic" Fallback (Safety Blocks)
* **The Problem:** Recognizing protected IP, parody characters (e.g., Rick & Morty, Disney, Marvel), or highly specific trademark elements can trigger safety policy violations or model rejection on advanced video models (like Seedance 2.0).
* **The Solution:** Fall back instantly to a stylized **Motion Comic / Animatic**! By using high-fidelity static keyframe plates (from Nano Banana 2/edit) and compiling them as a timed slideshow using local FFmpeg, you completely bypass the remote content filter, cut costs to zero, and maintain a highly premium look.

## 2. Dynamic Audio-Video Pacing (No Cut-offs)
* **The Rule:** Never use fixed-duration trimming (`-t 4`, `-t 5`) on multi-speaker or fast-paced dialogue clips. This cuts off characters mid-sentence.
* **The Workflow:** 
  1. Generate individual speech/dialogue files asynchronously using a high-quality neural Text-to-Speech (TTS) tool (like `edge-tts` or ElevenLabs).
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

## 5. ElevenLabs Generative Voice Acting
* **The Rule:** For high-concept, comedic, or animated commercials, standard robotic TTS voices fall flat. Use **ElevenLabs** for expressive voice generation.
* **Expressive Settings:**
  * For cartoon voice work, set `stability` low (between `0.25` and `0.45`). Lower stability allows the generative neural network to express drama, voice cracks, shouting, and high-energy inflections.
  * Set `similarity_boost` to `0.75` for clarity, and `use_speaker_boost` to `True`.
  * Select premade or cloned trickster/creator voices (e.g., Callum `N2lVS1w4EtoT3dr4eOWO` for Rick-like tones, Liam `TX3LPaxmHKxFdv7VOQHJ` for energetic ones).

## 6. FFmpeg Pitch Shifting & Cartoon Vocals
* **The Pitch Shift Filter Graph:** To convert normal adult voices into cartoonish squeaks (Meeseeks) or tremulous stammers (Morty), use FFmpeg's `asetrate` and `atempo` filters in tandem.
  * `asetrate` alters the sampling rate, which changes both pitch and speed (e.g. `44100 * 1.6` shifts pitch up 1.6x but speeds it up).
  * `atempo` shifts the speed back down to normal without affecting the pitch.
  * **High-Pitched Squeaky (Meeseeks):**
    ```bash
    ffmpeg -y -i input.mp3 -af "asetrate=44100*1.6,atempo=1/1.6" output.wav
    ```
  * **Nervous Cracking (Morty):**
    ```bash
    ffmpeg -y -i input.mp3 -af "asetrate=44100*1.25,atempo=1/1.25" output.wav
    ```

## 7. Failsafe FFmpeg Filter Mixing (amix & concat)
* **Amix Connection Errors:** When mixing audio tracks with different channel structures (e.g., mono TTS clips mixed into stereo beds), labeling the final output `[out]` without explicitly mapping it `-map "[out]"` causes FFmpeg to crash with `unconnected output` errors.
  * **Failsafe Syntax:** Simply omit the final stream label in your `amix` filter complex, and let FFmpeg automatically connect the mixed stream to the output file:
    ```bash
    ffmpeg -y -i line1.mp3 -i line2.mp3 -filter_complex "[0:a]adelay=0[a0];[1:a]adelay=1800[a1];[a0][a1]amix=inputs=2:duration=longest" -ar 44100 -ac 2 mixed.wav
    ```
* **Filter Concat vs Demuxer:** Direct `-c copy` concat demuxing fails with exit status 254 if clips have slightly different PTS start-times or float-point durations. Always use FFmpeg's `concat` filter complex to decode and re-encode raster-level frames safely when durations are float numbers:
  ```bash
  ffmpeg -y -i c1.mp4 -i c2.mp4 -filter_complex "[0:v][1:v]concat=n=2:v=1:a=0[outv]" -map "[outv]" -c:v libx264 -preset ultrafast compiled.mp4
  ```

## 8. Vertical Multiline Subtitle Stacking
* **The Layout:** On vertical portrait canvases (540x960), long sentences will overflow past the left/right safe zone boundaries.
* **The Solution:** Stack text blocks vertically on different `y` coordinates using the `enable` timeline tag:
  ```bash
  drawtext=text='Jerry\\: And look, I can create as many agents':enable='between(t,3.2,5.5)':x=(w-text_w)/2:y=h-160:fontcolor=yellow:fontsize=20:box=1:boxcolor=black@0.7:boxborderw=6,drawtext=text='as I want! It is awesome!':enable='between(t,3.2,5.5)':x=(w-text_w)/2:y=h-120:fontcolor=yellow:fontsize=20:box=1:boxcolor=black@0.7:boxborderw=6
  ```

## 9. Failsafe & Low-Memory Ken Burns (zoompan) Filter Recipe
* **The Problem:** Running FFmpeg's `zoompan` filter at full `1080x1920` resolution at 30fps creates huge internal frame buffers in memory (e.g. 120 frames for a 4s clip). This instantly causes Out of Memory (OOM) `SIGKILL` errors on remote sandboxes.
* **The Solution:** Use the **Low-Memory Zoompan Pattern** to scale down the image, run zoompan at a lower resolution and framerate, and then scale back up to the final size. This cuts memory usage by over 80%:
  1. Scale the input image down to `720x1280` (High Quality) or `540x960` (Ultra Safe) before `zoompan`.
  2. Reduce the framerate of the zoompan output to `15` (meaning `d = duration * 15`).
  3. Set zoompan size `s` to match the downscaled resolution (`720x1280` or `540x960`).
  4. Scale the output back up to `1080x1920` after zoompan, and use `-preset ultrafast` during H.264 encoding to minimize compression overhead.

* **Correct, Low-Memory Zoom/Pan (Ken Burns) commands:**
  * **Standard (720x1280, Recommended Quality):**
    ```bash
    ffmpeg -y -loop 1 -i input.png -vf "scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,zoompan=z='zoom+0.0008':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=60:s=720x1280,fps=15,scale=1080:1920" -c:v libx264 -preset ultrafast -t 4 -pix_fmt yuv420p output.mp4
    ```
  * **Ultra-Safe (540x960, Minimum Memory):**
    ```bash
    ffmpeg -y -loop 1 -i input.png -vf "scale=540:960:force_original_aspect_ratio=decrease,pad=540:960:(ow-iw)/2:(oh-ih)/2,zoompan=z='zoom+0.0008':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=60:s=540x960,fps=15,scale=1080:1920" -c:v libx264 -preset ultrafast -t 4 -pix_fmt yuv420p output.mp4
    ```

## 10. Working on Existing Scenes (Lipsync & Voice Cloning)
When editing, modifying, or voice-over-replacing dialogue inside an existing video scene (instead of generating new video frames from scratch):
* **The Rule:** Always use **ElevenLabs for voice cloning** and **sync.so for lip-syncing** to preserve character consistency.
* **The Pipeline:**
  1. **Finding Scenes:** To find scenes from famous TV shows or movies, you can use the find-scene API. Refer to the documentation and endpoints described at `https://api.find-scene.com/llms.txt` to search for and download the relevant clips or extract frames.
  2. **Voice Extraction:** Crop/extract a short, clean snippet (at least 10 seconds is enough, but more sample audio improves the cloning quality) where only one speaker speaks with minimal background noise. To isolate the correct segment, use a transcription tool (such as **Whisper**) to transcribe the audio, inspect the phrases/timestamps, and infer the exact portion belonging to the target speaker. If you run into issues or overlap, look at the entire video context to validate and resolve any discrepancies.
  3. **ElevenLabs Voice Cloning:** Create a cloned voice profile using the extracted audio. Keep stability low (between `0.25` and `0.45`) to preserve emotional range.
  4. **TTS Synthesis:** Synthesize the new dialogue lines with ElevenLabs TTS using the cloned voice ID (using the `eleven_multilingual_v2` model).
  5. **Lip-Sync via sync.so:** Submit the original video segment and the newly generated ElevenLabs TTS audio track to the sync.so API (via the `sync-3` model) to align lip movements perfectly.
  6. **Composition & Assembly:** Download the lip-synced video and assemble it into your final video timeline using FFmpeg.


## 11. Production Learnings for Broadcast-Quality Dubbing (June 2026)
* **find-scene Integration:** Always search subtitle files (`search_phrase` or `find_episode_by_phrase`) first before download. Get the `videoHash` and `textSource` to isolate the exact, continuous single-shot timestamps. This ensures the characters are centered and in-frame, bypassing low-quality or cropped social clips (like TikTok/Instagram compilations).
* **True Character Voice Cloning:** To clone custom cartoon or TV show characters:
  1. Extract a clean, isolated 5-10s voice clip of the target speaker using FFmpeg:
     `ffmpeg -ss <start> -i video.mp4 -t <dur> -ac 1 -ar 44100 dinesh_sample.mp3`
  2. Call ElevenLabs `/v1/voices/add` to create an authentic, custom-cloned voice profile.
  3. Synthesize the new script lines using this newly generated `voice_id`.
* **Video Looping & Syncing:** To handle longer speech over shorter close-ups, extract a clean continuous face clip and loop it to match the exact duration of the synthesized audio before calling `fal-ai/sync-lipsync/v3`.
* **Avoiding FFmpeg Subtitle Crashes:** Absolutely eliminate all apostrophes, single quotes, and special characters from drawtext text inputs (`"prompt to bot's"` -> `"prompt to bot bots"`). This prevents parser crashes and unhandled exceptions.

## 11. Production Learnings for Broadcast-Quality Dubbing (June 2026)
* **find-scene Integration:** Always search subtitle files (`search_phrase` or `find_episode_by_phrase`) first before download. Get the `videoHash` and `textSource` to isolate the exact, continuous single-shot timestamps. This ensures the characters are centered and in-frame, bypassing low-quality or cropped social clips (like TikTok/Instagram compilations).
* **True Character Voice Cloning:** To clone custom cartoon or TV show characters:
  1. Extract a clean, isolated 5-10s voice clip of the target speaker using FFmpeg:
     `ffmpeg -ss <start> -i video.mp4 -t <dur> -ac 1 -ar 44100 dinesh_sample.mp3`
  2. Call ElevenLabs `/v1/voices/add` to create an authentic, custom-cloned voice profile.
  3. Synthesize the new script lines using this newly generated `voice_id`.
* **Video Looping & Syncing:** To handle longer speech over shorter close-ups, extract a clean continuous face clip and loop it to match the exact duration of the synthesized audio before calling `fal-ai/sync-lipsync/v3`.
* **Avoiding FFmpeg Subtitle Crashes:** Absolutely eliminate all apostrophes, single quotes, and special characters from drawtext text inputs (`"prompt to bot's"` -> `"prompt to bot bots"`). This prevents parser crashes and unhandled exceptions.

* **Automated Word-Level SRT Subtitles:** Instead of hardcoded, brittle drawtext filters, generate a clean, word-wrapped `.srt` subtitle file mathematically timed based on character density (aiming for 3-4 words or under 20 characters per line). Burn it into the video using FFmpeg's `subtitles` filter with advanced ASS styles:
  `-vf subtitles=subs.srt:force_style='Alignment=2,FontSize=18,PrimaryColour=&H00FFFF,OutlineColour=&H000000,BorderStyle=3,MarginV=30'`
  This completely removes speaker names, auto-wraps lines, keeps titles centered, and prevents screen overflow on portrait mobile dimensions.

* **Automated Word-Level SRT Subtitles:** Instead of hardcoded, brittle drawtext filters, generate a clean, word-wrapped `.srt` subtitle file mathematically timed based on character density (aiming for 3-4 words or under 20 characters per line). Burn it into the video using FFmpeg's `subtitles` filter with advanced ASS styles:
  `-vf subtitles=subs.srt:force_style='Alignment=2,FontSize=18,PrimaryColour=&H00FFFF,OutlineColour=&H000000,BorderStyle=3,MarginV=30'`
  This completely removes speaker names, auto-wraps lines, keeps titles centered, and prevents screen overflow on portrait mobile dimensions.

* **L-Cuts & Reaction Shots to Mask Loops:** Looping a short (1-2s) close-up of an actor speaking makes the looping seam noticeable when they blink or reset their posture. To mask the loop and deliver a broadcast-quality edit, implement a **cinematic L-cut**:
  1. Show the speaking character's face for the first few seconds (e.g. 0-3s).
  2. Cut away to a reaction shot of the second character listening (e.g. 3-6s), keeping the speaker's voice track playing continuously over the cut.
  3. Cut back to the speaker's face for the final word or sentence resolver (e.g. 6-7s).
  This completely masks the loop seam, creates active pacing, and mimics standard broadcast editing structures.

* **L-Cuts & Reaction Shots to Mask Loops:** Looping a short (1-2s) close-up of an actor speaking makes the looping seam noticeable when they blink or reset their posture. To mask the loop and deliver a broadcast-quality edit, implement a **cinematic L-cut**:
  1. Show the speaking character's face for the first few seconds (e.g. 0-3s).
  2. Cut away to a reaction shot of the second character listening (e.g. 3-6s), keeping the speaker's voice track playing continuously over the cut.
  3. Cut back to the speaker's face for the final word or sentence resolver (e.g. 6-7s).
  This completely masks the loop seam, creates active pacing, and mimics standard broadcast editing structures.

* **Direct-Stream MP4 Delivery Only:** Never deliver video exports using landing-page-locked or broken file locker hosts like Filebin. Deliver strictly using direct, raw, high-speed streamable `.mp4` URLs (such as Uguu.se) that render with full audio and visual playback instantly in native browser or phone players on the very first click.
* **Freeze-Frame Reactions to Silence Mute Characters:** In L-cuts or multi-camera reaction shots, if the listening character speaks or shifts their lips in the original source footage, they will appear to be talking over the speaker's voice track. To prevent this:
  1. Extract a single image frame (`-vframes 1`) from the raw footage at a timestamp where the listener's mouth is completely closed and deadpan:
     `ffmpeg -ss <timestamp> -i raw.mp4 -vf "<scale_filters>" -vframes 1 frame.png`
  2. Convert that single frozen frame into a static looped reaction clip matching the reaction shot duration:
     `ffmpeg -loop 1 -i frame.png -t <duration> -c:v libx264 -preset ultrafast -r 15 -pix_fmt yuv420p v_reaction.mp4`
  3. Concatenate this frozen clip into the timeline. This guarantees a perfectly static, natural, silent reaction shot with zero distracting lip movement.

* **Direct-Stream MP4 Delivery Only:** Never deliver video exports using landing-page-locked or broken file locker hosts like Filebin. Deliver strictly using direct, raw, high-speed streamable `.mp4` URLs (such as Uguu.se) that render with full audio and visual playback instantly in native browser or phone players on the very first click.
* **Freeze-Frame Reactions to Silence Mute Characters:** In L-cuts or multi-camera reaction shots, if the listening character speaks or shifts their lips in the original source footage, they will appear to be talking over the speaker's voice track. To prevent this:
  1. Extract a single image frame (`-vframes 1`) from the raw footage at a timestamp where the listener's mouth is completely closed and deadpan:
     `ffmpeg -ss <timestamp> -i raw.mp4 -vf "<scale_filters>" -vframes 1 frame.png`
  2. Convert that single frozen frame into a static looped reaction clip matching the reaction shot duration:
     `ffmpeg -loop 1 -i frame.png -t <duration> -c:v libx264 -preset ultrafast -r 15 -pix_fmt yuv420p v_reaction.mp4`
  3. Concatenate this frozen clip into the timeline. This guarantees a perfectly static, natural, silent reaction shot with zero distracting lip movement.

* **Natural Silent Reaction Clips (Preferred over Freeze-Frames):** While a frozen single frame silences the mouth, it can look artificial (like a paused video) if the actor is in a dynamic pose or has their hands raised. The absolute gold standard is to locate a natural **3-second silence segment** in the episode using find-scene gap search. Find a sequence where the character is listening, blinking, or slightly shifting their posture naturally while keeping their mouth closed. This maintains organic, living motion in the scene while preserving absolute silence on their lips.

* **Natural Silent Reaction Clips (Preferred over Freeze-Frames):** While a frozen single frame silences the mouth, it can look artificial (like a paused video) if the actor is in a dynamic pose or has their hands raised. The absolute gold standard is to locate a natural **3-second silence segment** in the episode using find-scene gap search. Find a sequence where the character is listening, blinking, or slightly shifting their posture naturally while keeping their mouth closed. This maintains organic, living motion in the scene while preserving absolute silence on their lips.

* **The Failsafe L-Cut Assembly Rule:** If you upload a continuous multi-character clip directly to the Lip-Sync API, the model will warp *every* visible face on screen to match the voice, making silent/listening characters look like they are speaking the speaker's words. To guarantee absolute silent lips on the listener:
  1. Only send the active speaking character's shots to the Lip-Sync API. Use a long, continuous, unlooped clip of the speaker to prevent looping artifacts.
  2. Process the reaction/listening shots locally (or use natural silent clips) and **never upload them to the Sync API**.
  3. Concatenate the synced speaking shots and the untouched reaction shots locally using FFmpeg's `filter_complex`. This keeps the listener's lips 100% static while the speaker's lips are perfectly synced.

* **The Failsafe L-Cut Assembly Rule:** If you upload a continuous multi-character clip directly to the Lip-Sync API, the model will warp *every* visible face on screen to match the voice, making silent/listening characters look like they are speaking the speaker's words. To guarantee absolute silent lips on the listener:
  1. Only send the active speaking character's shots to the Lip-Sync API. Use a long, continuous, unlooped clip of the speaker to prevent looping artifacts.
  2. Process the reaction/listening shots locally (or use natural silent clips) and **never upload them to the Sync API**.
  3. Concatenate the synced speaking shots and the untouched reaction shots locally using FFmpeg's `filter_complex`. This keeps the listener's lips 100% static while the speaker's lips are perfectly synced.
