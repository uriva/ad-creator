# Automated Topic-to-Video & Claude-Code Explainer Pipeline

This guide outlines the system architecture and production guidelines for the **Topic-to-Video / Claude-Code Explainer Video** pipeline. Developed for high-volume, automated creation, this workflow transforms a single input topic into a fully edited, captioned, and narrated video (typical duration: 30–60s) for less than the cost of a cup of coffee.

---

## 1. System Architecture: "Topic In, Finished Video Out"

The pipeline operates as an autonomous agent-driven workflow (using Claude Code as the orchestration brain) to process content sequentially through six automated stations:

```
                  ┌────────────────────────────────────────┐
                  │             1. INPUT TOPIC             │
                  └───────────────────┬────────────────────┘
                                      ▼
                  ┌────────────────────────────────────────┐
                  │      2. RESEARCH & SCRIPT GENERATION   │
                  └───────────────────┬────────────────────┘
                                      ▼
                  ┌────────────────────────────────────────┐
                  │         3. CUSTOM VOICE DESIGN         │
                  └───────────────────┬────────────────────┘
                                      ▼
                  ┌────────────────────────────────────────┐
                  │      4. WORD-BY-WORD WHISPER SUBS      │
                  └───────────────────┬────────────────────┘
                                      ▼
                  ┌────────────────────────────────────────┐
                  │   5. AUDIO DUCKING & B-ROLL DIRECTING  │
                  └───────────────────┬────────────────────┘
                                      ▼
                  ┌────────────────────────────────────────┐
                  │    6. HYPERFRAMES / FFMPEG ASSEMBLY    │
                  └────────────────────────────────────────┘
```

---

## 2. Pipeline Stages & Production Standards

### Stage 1: Research-Backed Scripting & Structure
* **The Rule of Grounding**: Never allow the AI to fabricate statistics, historical data, or factual claims. **Every fact, figure, or claim must be backed by live web search / research** (using search-enabled agents).
* **The Tone**: Write in highly conversational, localized, natural spoken language (e.g., spoken Hebrew as outlined in the reference video) instead of formal, literary text. Use simple, direct sentences.
* **The Pacing**: Structure the shooting script with a clear division of spoken voiceover (VO) and visual directives (B-roll/screen instructions) for each section:
  * **Hook (0:00–0:05)**: A highly engaging, fast-paced opening statement to capture attention.
  * **Context / Problem (0:05–0:20)**: Introduce the core topic, why it matters, and map the key concepts.
  * **Content / Core Explanation (0:20–0:45)**: Step-by-step breakdown using concrete analogies.
  * **CTA & Outro (0:45–0:60)**: Clear action step (e.g., joining a community, subscribing, visiting a link).

### Stage 2: Custom Voice Design (ElevenLabs)
* **The Problem**: Standard robotic Text-to-Speech (TTS) voices are immediately recognized by viewers and platforms, resulting in low retention and algorithmic suppression.
* **The Solution**: Use **ElevenLabs Voice Design** to generate a bespoke, customized voice profile. Describe the desired speaker traits (gender, age, accent, specific vocal texture) to create a unique and realistic voice identity.
* **Dynamic Range Settings**: Set `stability` low (between `0.25` and `0.45`) during TTS generation. This forces the model to inject human-like vocal variety, organic pacing, emotional inflections, and realistic micro-pauses.

### Stage 3: Automated Word-Level Subtitles (Whisper)
* **Word-by-Word Alignment**: Use OpenAI's **Whisper** (running locally on the machine for zero cost) to transcribe the generated speech and capture the exact milliseconds each word begins and ends.
* **Mobile Portrait Layout Guidelines (9:16)**:
  * Long sentences must be split. Keep subtitle entries extremely compact: **3–4 words or under 20 characters per line**.
  * Auto-wrap lines to prevent horizontal overflow.
  * Burn subtitles using FFmpeg's `subtitles` filter with high-contrast, centered ASS styles (e.g., yellow or bold white text with a thick black outline).

### Stage 4: Intelligent Audio Ducking
* **The Soundscape**: A professional video must have a music bed that complements the speaker without overpowering them. Select an ambient track matching the video's mood from royalty-free libraries.
* **Automated FFmpeg Ducking**: Apply a sidechain-like volume filter complex. Automatically lower the background music by **8 to 12 dB** whenever the speaker is speaking, and raise it back to full level during pauses/silence:
  ```bash
  # Example FFmpeg sidechain gate / ducking complex (substitute parameters accordingly)
  ffmpeg -y -i vo.mp3 -i music.mp3 -filter_complex "[0:a]asplit[vo1][vo2];[vo1]volume=1.0[vo_mix];[vo2]pan=1c|c0=c0,compand=attacks=0.01:decays=0.1:points=-40/-40|-30/-30|-20/-20|-10/-25|0/-35[duck_trigger];[1:a][duck_trigger]sidechaincompress=threshold=0.1:ratio=4[music_ducked];[vo_mix][music_ducked]amix=inputs=2:duration=first" -ac 2 -ar 48000 output.wav
  ```

### Stage 5: Intelligent B-Roll Selection & Directing
To keep the visual track active and engaging, the automated "AI Director" selects or generates visual content for each script section using three sources:
1. **Free Stock Footage**: Programmatically fetch matching lifestyle or technical clips from high-quality stock libraries (e.g., Pexels, Pixabay).
2. **AI-Generated Video Clips**: For highly dramatic or specific visual moments, prompt **Seedance 2.0** to generate custom 4-second video clips.
3. **AI-Generated Stills + Low-Memory Zoompan**: For standard conceptual beats, generate static images with **Nano Banana 2** and apply a Ken Burns pan-and-zoom effect to keep them visually alive.
   * *Safety Rule*: To prevent Out-of-Memory (OOM) crashes during rendering, always downscale the keyframe to `720x1280` or `540x960` before applying the `zoompan` filter, then scale back to full portrait resolution:
     ```bash
     ffmpeg -y -loop 1 -i still.png -vf "scale=540:960:force_original_aspect_ratio=decrease,pad=540:960:(ow-iw)/2:(oh-ih)/2,zoompan=z='zoom+0.0008':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=60:s=540x960,fps=15,scale=1080:1920" -c:v libx264 -preset ultrafast -t 4 -pix_fmt yuv420p output.mp4
     ```

### Stage 20% Rule: The Human Touch
* Fully automated videos risk sounding generic, which video-sharing platforms easily detect and downrank.
* To achieve viral, high-performing retention, **always keep a "20% Human Touch" phase**. The human creator must:
  1. Define and select the core video topic.
  2. Review and refine the script, adding personal perspective, humor, or unique angles that an AI cannot replicate.
  3. Validate visual continuity and final emotional resonance before rendering.

---

## 3. Automated Compilation & Rendering (HyperFrames)

Once all files (subtitles, audio voiceovers, ducked music tracks, stock footage, Ken Burns clips, and brand logo overlays) are generated, the system compiles them into a single broadcast-ready `.mp4` using the `HyperFrames` npm library or local FFmpeg within approximately 8 minutes without any manual editing.

* **Asset Delivery**: Ensure that finalized video exports are saved in `/tmp` during processing to bypass FUSE latency bottlenecks, and then uploaded to a high-speed direct streamable URL (e.g., `Uguu.se` or S3) to guarantee immediate playback with full audio in any native web player.
