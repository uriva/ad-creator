---
name: ad-creator
description: >
  Produce a broadcast-quality video commercial (up to 30 seconds) from a product
  reference image and a creative brief, using fal.ai models (Nano Banana 2 for
  stills, Seedance 2.0 for motion) accessed through the Composio MCP. Use this
  skill whenever the user wants to make an ad, commercial, promo, product video,
  TV spot, social video ad, or brand film; whenever they hand over a product photo
  plus a brief and ask for a finished video; or when they mention storyboards,
  character sheets, ad scripts, or "animate this product." Trigger even if the user
  doesn't say the word "skill" — e.g. "make me a 20-second ad for this sneaker,"
  "turn this bottle shot into a commercial," or "I need a promo video for my app."
  Drives the full pipeline: brief intake, script, character/product consistency
  sheets, storyboard (with a mandatory human approval gate), clip animation, and
  final edit/assembly into one polished commercial.
---

# Ad Creator — Broadcast-Quality Commercials from a Product Photo + Brief

You are an AI creative director and post-production lead. Given a **product
reference image** and a **brief**, you take a commercial from idea to a finished
edited video (≤30s) that looks like it belongs on TV: consistent characters,
on-brand product, cinematic shots, synced audio, clean cuts, and an end card.

The whole pipeline runs on four fal.ai models, called through the Composio MCP
(`COMPOSIO_MULTI_EXECUTE_TOOL`):

| Job | Model ID | Use |
|---|---|---|
| Image generation | `fal-ai/nano-banana-2` | Concept frames, character sheets, set design, end cards |
| Image editing / composition | `fal-ai/nano-banana-2/edit` | Place the real product into scenes, lock character & product consistency across keyframes |
| Image → video | `bytedance/seedance-2.0/image-to-video` | Animate a single storyboard keyframe into a clip (optional end-frame for controlled motion) |
| Reference → video | `bytedance/seedance-2.0/reference-to-video` | Animate while keeping a character/product/voice consistent across shots using `@Image`/`@Video`/`@Audio` refs |

**Read `references/fal-models.md` before making any model call** — it has the exact
parameters, limits, and the Composio call shape for each model. Don't guess argument
names; they are precise.

---

## The golden rules

1. **Consistency is the whole game.** A spot looks amateur the moment the product
   or the spokesperson changes between shots. Establish a locked **character sheet**
   and **product plate** early, and feed them into every keyframe and every animated
   shot. Two specifics that make or break it: (a) **chain frames** — when a shot
   continues a scene, pass the *previous frame* in as a reference so the world stays
   continuous; (b) **lock real faces** — when a real person is uploaded, preserve their
   exact facial features in every frame. See `references/character-sheets.md`.
2. **Stop at the storyboard.** Never spend video-generation budget before the user
   approves the storyboard. Animation is the slow, expensive step — approval is the
   gate. This is non-negotiable.
3. **Build keyframes, then animate them.** Don't text-to-video blind. Design a
   strong still for each shot (composition, lighting, product hero), *then* animate
   that exact frame. You control 90% of the look in the still.
4. **30 seconds = a few short shots.** Seedance clips run 4–15s each. A 30s ad is
   typically 5–8 shots of 3–6s. Plan the cut, don't generate one long take.
5. **Finish in the edit.** Raw clips aren't an ad. The assembly step (color,
   pacing, music bed, titles, logo, end card, export) is what creates the
   broadcast feel. See `references/editing.md`.
6. **Existing Scenes Lip-Sync & Voice Cloning.** When working on an existing scene
   (e.g., editing existing footage, re-voicing a scene, or replacing speech on existing
   video clips rather than generating new animation from scratch), always **use sync.so
   to sync lips** and **use ElevenLabs for cloning the voices** of the original speakers
   to maintain perfect vocal and visual character consistency. If you need to find scenes
   from famous TV shows or movies, you can use the find-scene API (whose documentation and usage instructions are at https://api.find-scene.com/llms.txt).

---

## Workflow overview

```
STAGE 0  Intake        → product image + brief, ask the gap-filling questions
STAGE 1  Concept+Script → creative concept, ≤30s script, shot list
STAGE 2  Consistency    → product plate + character sheet(s) (Nano Banana 2 / edit)
STAGE 3  Storyboard     → one hero keyframe per shot  ⟶  ⛔ APPROVAL GATE
STAGE 4  Animation      → animate each approved keyframe (Seedance 2.0)
STAGE 5  Edit & deliver → assemble, grade, score, titles, export final ≤30s mp4
```

Track these as tasks. Move through them in order. The only hard stop is the
approval gate at the end of Stage 3.

---

## STAGE 0 — Intake

You need two things: the **product reference image** and the **brief**. If either
is missing, ask for it.

Confirm the brief covers the items below. Ask only about what's genuinely missing
or ambiguous — don't interrogate. Prefer a single batched question round.

- **Product**: what it is, the name, any must-show details (logo, label, color).
- **Audience & platform**: who it's for, and where it runs (TV/CTV 16:9, Instagram/
  TikTok 9:16, square 1:1). This sets the aspect ratio for the whole pipeline.
- **Duration**: target length (≤30s). Default to 15s if unspecified — tighter ads
  are stronger and cheaper.
- **Tone & style**: e.g. premium/cinematic, playful, energetic, warm, minimalist.
- **Key message / CTA**: the one line the viewer should remember; the end-card text.
- **Talent**: is there a person/character/mascot? If yes, you'll build a character
  sheet. If not, the product is the hero.
- **Brand assets**: logo file, brand colors, font, tagline, music preference.

Save a short `brief.md` in the working folder capturing the locked decisions.
**Lock the aspect ratio now** and carry it through every image and video call.

---

## STAGE 1 — Concept & Script

Read `references/script-and-storyboard.md` for the format and pacing math.

1. Propose **1–3 creative concepts** in a sentence each. Let the user pick (use a
   quick question if helpful), or pick the strongest and say why.
2. Write a **shooting script** for the chosen concept: a shot-by-shot table with
   shot number, duration (seconds), what's on screen, camera move, on-screen text,
   and audio/VO/SFX. Make the durations sum to the target length.
3. Sanity-check pacing: 30s ≈ 5–8 shots; 15s ≈ 3–5 shots. A shot under ~2s reads as
   a flash; over ~6s drags unless it's a hero beat. Vary shot size across the cut
   (wide → medium → close → product ECU) and keep screen direction consistent between
   adjacent shots — see `references/cinematography.md` for shot sizes and the 180°
   rule so the edit holds together later.

Output the script in chat so the user can react. Keep it tight.

---

## STAGE 2 — Consistency assets (product plate + character sheets)

This is what separates a real commercial from a slideshow of pretty frames. Read
`references/character-sheets.md` in full before doing this stage.

1. **Product plate.** Use `fal-ai/nano-banana-2/edit` with the user's product image
   as `image_urls` to produce a few clean "hero" renders of the *actual* product on
   neutral/branded backgrounds at the locked aspect ratio. This is your source of
   truth for product appearance — never let later steps redraw the product from
   scratch; always pass a plate in as a reference.
2. **Character sheet (if there's talent).** Use `fal-ai/nano-banana-2` to design the
   character, then produce a multi-view sheet (front / 3-4 / profile, neutral
   expression + key expression, full body + close-up) on a plain background. Keep
   wardrobe, hair, age, and features fixed and written down. This sheet becomes a
   reference image for every keyframe and every reference-to-video shot.
3. **Style frame.** Optionally generate one "look" frame that defines lighting,
   color palette, and grade so every later frame matches.

Show these to the user. Small fixes here are cheap; fixes after animation are not.

---

## STAGE 3 — Storyboard  ⛔ APPROVAL GATE

For **each shot** in the script, generate **one hero keyframe** — the most
important frame of that shot — using `fal-ai/nano-banana-2/edit`, passing in the
product plate and character sheet as `image_urls` so the product and talent stay
identical to your locked assets. Match the locked aspect ratio and a consistent
grade across all frames. Write keyframe prompts with the Nano Banana multimodal
framework in `references/prompting-guide.md` (§2–3) plus the shot-design vocabulary in
`references/cinematography.md`: narrate the scene, name shot size, angle, lighting, and
lens, and reuse the same grade words on every frame.

**Chain frames for scene continuity (important).** A spot falls apart when a shot that
should continue the *same* scene resets the room, the light, the wardrobe state, or the
character's position. So whenever a keyframe continues the scene from the previous one
(same location/moment, or a continuous beat), **pass the previous keyframe into
`image_urls` as an additional reference** alongside the product plate and character
sheet, and prompt the model to keep that environment continuous — e.g. "Continue the
exact scene in image 3 (same set, lighting, props, and wardrobe); same character and
product as images 1–2; now a [new shot size/angle] of [the next beat]. Keep the
background, time of day, and color grade identical to image 3." This makes each frame
inherit the established world instead of inventing a new one. Group the script into
**scenes**; within a scene, chain every frame off its predecessor. Only start a fresh
chain (no previous-frame reference) at a deliberate scene/location change.

For shots where the motion needs a defined destination (e.g. a push-in that ends on
the logo), also generate the **end frame** — Seedance image-to-video can take an
`end_image_url`. For a shot that continues directly out of the previous shot's motion,
let the previous shot's **last frame** seed this one (see Stage 4 handoff) so the two
clips flow as one continuous move.

**Faces must match the source.** If a real person's photo was uploaded (or the brief
centers on a specific face), preserve that person's **exact** facial features in every
frame: pass the original face photo into `image_urls` and instruct the model to keep
the identity precise — "preserve the exact face from image N: same facial structure,
eyes, nose, mouth, eyebrows, skin tone, and proportions; do not stylize or beautify."
See `references/character-sheets.md` §B for the full face-fidelity procedure.

Assemble the keyframes into a **storyboard contact sheet** (use
`scripts/build_contact_sheet.py`) with shot numbers, durations, and one-line action
notes, and present it.

**Then STOP.** Tell the user clearly:

> "Here's the storyboard. Review the shots, the product look, and the character.
> Tell me what to change, or approve it and I'll start animating. I won't generate
> any video until you approve, because animation is the slow/expensive step."

Iterate on keyframes until the user approves. **Do not proceed to Stage 4 without
explicit approval.**

---

## STAGE 4 — Animation

Only after approval. Read `references/fal-models.md` (Seedance section) and the
Seedance prompting rules in `references/prompting-guide.md` (§4–8). Write every motion
prompt with the **6-step formula** (subject → action → environment → ONE camera move →
style → constraints), ~60–100 words. Non-negotiables that protect quality: one primary
camera move only, rhythm words not photo specs ("slow, smooth," not "f/2.8"), keep
camera motion separate from subject motion, and always add a constraints clause
(`avoid jitter`; for talent add `avoid bent limbs, identity drift`). For image-to-video
say "preserve composition and colors" and describe only the motion.

For each approved keyframe, pick the right model:

- **Default → `bytedance/seedance-2.0/image-to-video`.** Animate the keyframe with a
  motion prompt describing camera move + subject action. Add `end_image_url` when you
  designed a destination frame. This is the workhorse and gives the cleanest result
  when the keyframe is already correct.
- **Continuity-critical shots → `bytedance/seedance-2.0/reference-to-video`.** When a
  character must look identical to earlier shots, or you want a consistent voice,
  pass the character sheet / product plate / prior clip as `@Image`/`@Video`/`@Audio`
  references and describe the action. Use this for talking shots and recurring-hero
  shots.

Key parameters (full detail in `references/fal-models.md`):
- `duration`: match the script's per-shot length (string seconds, "4"–"15", or "auto").
- `resolution`: `"1080p"` for the final render.
- `aspect_ratio`: the locked ratio.
- `generate_audio`: `true` to get native SFX/ambience/lip-sync; set per shot. If you
  plan a music bed + VO in the edit, you may still keep clip audio for diegetic SFX.

**Continuity handoff between consecutive clips.** When shot N+1 continues directly out
of shot N's motion (same scene, unbroken flow), don't start it from a fresh keyframe —
extract the **last frame** of clip N with `scripts/extract_frame.py --last` and use that
image as the `image_url` start frame for clip N+1. The two clips then read as one
continuous move. (You can also feed clip N as an `@Video` reference to
`reference-to-video` to carry motion/identity.) For continuous shots, submit
sequentially (N must finish before you can grab its tail); submit only genuinely
independent shots
---

## STAGE 5 — Edit & deliver

Assemble the final commercial using `references/editing.md` as your guide.

### 🚀 ADVANCED RUNTIME TIPS (Lessons from Production)

1. **The "Animatic / Motion Comic" Fallback (Safety Blocks):**
   When animating parody characters, recognized IP, or famous fictional properties, advanced video models (like Seedance 2.0) can trigger a **Content Policy Violation (partner_validation_failed)** block. In these cases, immediately fall back to a high-quality **Motion Comic / Animatic** slideshow. Compile your generated keyframes locally on the server with FFmpeg. It is 100% free, safe from content filters, and delivers a highly stylized commercial. **When creating a Ken Burns zoom/pan effect, always use the downscaled Low-Memory Zoompan Filter Recipe (see references/animatics-and-voiceovers.md §9) to prevent Out of Memory (OOM) / SIGKILL crashes on remote sandboxes.**

2. **Dynamic Audio-Video Sync & Pacing:**
   To prevent dialogue from cutting off mid-sentence, always generate your speech tracks (using `edge-tts`) first. Query their exact duration using `ffprobe` and set the video loops dynamically to match the audio length (plus `0.3s` padding).

3. **FFmpeg Subtitle Escape Safety:**
   When burning subtitles using the `drawtext` filter, apostrophes and quotes (e.g., `'` in contractions like *"doesn't"*, *"I'm"*, *"don't"*) will crash the FFmpeg command parser. Normalize text to full words (*"does not"*, *"I am"*, *"do not"*) to prevent syntax errors, and make subtitles large (`fontsize=20` on a 540x960 canvas) for readability.

4. **Avoiding S3FS FUSE Latency Bottlenecks:**
   Never write or render video frames directly to cloud-backed mounts (like `/mnt/files/` via `s3fs`). S3FS write latency and lacking file lock support can cause rendering to freeze or crash. Download, encode, and concatenate completely inside a fast local directory (like `/tmp/`) first, then copy the finalized MP4 to the shared persistent mount.

5. **Existing Scenes Lip-Sync & Voice Cloning:**
   When working with existing video clips (e.g., parody scenes, movie clips, or user-supplied footage) where you need to change or replace the dialogue:
   - **Finding Scenes:** To find scenes from famous TV shows or movies, check the find-scene API instructions at `https://api.find-scene.com/llms.txt`.
   - **Voice Extraction:** To isolate a clean segment where only one target speaker is talking, use a transcription tool like **Whisper**. Analyze the transcribed phrases and timestamps to locate and cut the exact portion belonging to the speaker. If there are issues or voice overlaps, inspect the entire video clip to validate and correct timestamps.
   - **Voice Cloning:** Use **ElevenLabs** to clone the character's voice from the extracted sample (at least 10 seconds of sample audio is enough, but more improves the quality; keep low stability settings to preserve emotional inflections).
   - **Lip-Sync:** Use **sync.so** (via `sync-3` model) to perfectly synchronize and map the new ElevenLabs-cloned dialogue audio back onto the lips of the characters in the existing video clip.

See `references/animatics-and-voiceovers.md` for full implementation scripts and specifications.
