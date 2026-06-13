# fal.ai Models — Parameters, Limits & Composio Call Patterns

All four models are reached through the **Composio MCP**, not direct HTTP. You call
`COMPOSIO_MULTI_EXECUTE_TOOL` with one of the fal executor tools and a `tool_slug`.
Argument names below are exact — copy them.

## Table of contents
1. How calls work (sync vs async)
2. `fal-ai/nano-banana-2` — text → image
3. `fal-ai/nano-banana-2/edit` — image edit / composition
4. `bytedance/seedance-2.0/image-to-video`
5. `bytedance/seedance-2.0/reference-to-video`
6. Output shapes & downloading
7. Cost / budget discipline

---

## 1. How calls work

Two execution styles, both via `COMPOSIO_MULTI_EXECUTE_TOOL`:

**Synchronous (use for images — they finish in seconds):**
`FAL_AI_RUN_MODEL_SYNC` with `{ "model_id": "...", "input": { ... } }`. Returns the
result inline under `data.images`.

**Asynchronous (use for video — it can take minutes):**
1. `FAL_AI_SUBMIT_ASYNC_JOB` with `{ "model_id": "...", "input": { ... } }` → returns a `request_id`.
2. `FAL_AI_QUEUE_GET_STATUS` with `{ "model_id": "...", "request_id": "..." }` → poll until `status` is `COMPLETED`.
3. `FAL_AI_GET_QUEUE_REQUEST_RESULT` with `{ "model_id": "...", "request_id": "..." }` → returns the final `data.video.url`.

Known pitfalls (observed):
- Prefer `FAL_AI_RUN_MODEL_SYNC` for short image jobs; avoid `FAL_AI_SUBSCRIBE_ASYNC_JOB` (has returned HTTP 405 during polling).
- Always validate `data.images` is non-empty before reading `data.images[0].url`.
- For queued video, the final URL appears in `FAL_AI_GET_QUEUE_REQUEST_RESULT`, not in intermediate status responses.
- **Parallelize**: put multiple independent submit/generate calls in a single
  `COMPOSIO_MULTI_EXECUTE_TOOL` `tools` array to run them at once.

If the toolkit isn't connected: `COMPOSIO_MANAGE_CONNECTIONS` with toolkit `fal_ai`.

---

## 2. `fal-ai/nano-banana-2` — text → image
Google's fast state-of-the-art image model. Use for character design, set/look
frames, end cards, and anything generated from scratch.

**Input** (`input` object):
| Field | Type | Notes |
|---|---|---|
| `prompt` | string **(required)** | 3–50000 chars. Describe scene, subject, lighting, lens, mood. |
| `aspect_ratio` | enum | `auto`,`21:9`,`16:9`,`3:2`,`4:3`,`5:4`,`1:1`,`4:5`,`3:4`,`2:3`,`9:16`,`4:1`,`1:4`,`8:1`,`1:8`. Default `auto`. **Set this to your locked ratio.** |
| `resolution` | enum | `0.5K`,`1K`,`2K`,`4K`. Default `1K`. Use `2K`/`4K` for hero/print frames. |
| `num_images` | int 1–4 | Default 1. Generate 2–4 to pick the best. |
| `output_format` | enum | `jpeg`,`png`,`webp`. Default `png`. |
| `seed` | int | Set to reproduce / hold a look. |
| `system_prompt` | string | Optional persona/style steer. |
| `thinking_level` | `minimal`/`high` | Optional; `high` for complex compositions. |
| `enable_web_search` | bool | Default false; lets the model pull current references. |
| `safety_tolerance` | "1"–"6" | "1" strictest, "6" loosest. Default "4". |

**Output:** `data.images[]` (each has `url`, `content_type`, …) and `data.description`.

---

## 3. `fal-ai/nano-banana-2/edit` — image edit / composition
Same model, image-conditioned. **This is the consistency engine.** Pass real images
in `image_urls` and it edits/composes while preserving them — e.g. drop the user's
actual product into a generated scene, or render a keyframe with your locked
character + product so they stay identical.

**Input** adds to the text→image fields:
| Field | Type | Notes |
|---|---|---|
| `prompt` | string **(required)** | The edit/composition instruction. |
| `image_urls` | string[] | URLs of reference/input images (product plate, character sheet, prior frame). Multiple allowed — combine them. Optional only if a `video_url`/`audio_url`/`pdf_url` is given. |
| `video_url` | string | Optional video context (http(s)/data URL ≤15MB, or YouTube URL). |
| `audio_url` | string | Optional audio context (≤15MB). |
| `pdf_url` | string | Optional PDF context (≤15MB). |
| `aspect_ratio`,`resolution`,`num_images`,`output_format`,`seed`,`system_prompt`,`thinking_level`,`enable_web_search`,`safety_tolerance` | | Same as §2. |

**Output:** identical shape to §2 (`data.images[]`, `data.description`).

**Consistency tip:** to lock a keyframe, pass *both* the product plate and the
character sheet in `image_urls`, then prompt: "Place [character from image 2] holding
[product from image 1] in [scene]; keep the product label, colors, and the
character's face/hair/wardrobe exactly as in the references."

---

## 4. `bytedance/seedance-2.0/image-to-video`
Animate a single still into a cinematic clip with native synchronized audio.
**The workhorse for animating storyboard keyframes.**

**Input:**
| Field | Type | Notes |
|---|---|---|
| `prompt` | string **(required)** | Motion description: camera move + subject action + mood. |
| `image_url` | string **(required)** | The starting frame (your approved keyframe). JPEG/PNG/WebP, ≤30MB. |
| `end_image_url` | string | Optional last frame — video transitions start→end. Great for controlled push-ins / reveals. |
| `duration` | enum string | `"auto"` or `"4"`–`"15"` seconds. Match the shot's scripted length. |
| `resolution` | enum | `480p`,`720p`,`1080p`. Default `720p`. Use `1080p` for final. |
| `aspect_ratio` | enum | `auto`,`21:9`,`16:9`,`4:3`,`1:1`,`3:4`,`9:16`. Lock it. |
| `generate_audio` | bool | Default true. Native SFX/ambience/lip-sync. Same cost either way. |
| `seed` | int | For reproducibility. |

**Output:** `data.video.url` (mp4) and `data.seed`.

---

## 5. `bytedance/seedance-2.0/reference-to-video`
Generate video guided by multiple references — keep a character, product, or voice
**consistent across shots**. Reference items are addressed in the prompt as
`@Image1`, `@Video1`, `@Audio1`, etc.

**Input:**
| Field | Type | Notes |
|---|---|---|
| `prompt` | string **(required)** | Reference `@Image1`/`@Video1`/`@Audio1` in the text. |
| `image_urls` | string[] | Up to **9** reference images (JPEG/PNG/WebP, ≤30MB each). |
| `video_urls` | string[] | Up to **3** reference videos (MP4/MOV, combined 2–15s, ≤50MB total, ~480p–720p). |
| `audio_urls` | string[] | Up to **3** reference audio (MP3/WAV, combined ≤15s, ≤15MB each). If audio is given, at least one image or video is required. |
| `duration` | enum string | `"auto"` or `"4"`–`"15"`. |
| `resolution` | enum | `480p`,`720p`,`1080p`. |
| `aspect_ratio` | enum | as §4. |
| `generate_audio` | bool | Default true. |
| `seed` | int | |

**Limit:** total files across all modalities ≤ **12**.

**Output:** `data.video.url` and `data.seed`.

⚠️ **Real faces:** Seedance reference inputs may reject identifiable real-person face
photos. Use a synthetic spokesperson built from the character sheet rather than a real
customer's face — safer and gives full consistency control.

**When to choose this over image-to-video:** talking-head/spokesperson shots,
recurring-hero shots where the face must match exactly, or when you want to carry a
voice or a motion style from a reference clip. For a clean keyframe with simple
camera motion, plain image-to-video is usually sharper and simpler.

---

## 6. Output shapes & downloading
- Images: `data.images[0].url`. Videos: `data.video.url`.
- **fal CDN URLs can expire.** Immediately download with `scripts/fetch_media.py`
  and reference local paths everywhere downstream (contact sheet, ffmpeg).

## 7. Cost / budget discipline
Every generation is billed. Be deliberate:
- Iterate cheaply on **images** (Stage 2–3), commit to **video** only after approval.
- Use `num_images` 2�