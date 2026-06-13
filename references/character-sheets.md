# Consistency: Product Plates & Character Sheets

Inconsistency is the #1 tell of amateur AI ads — a product whose label morphs, a
spokesperson whose face changes between shots. You prevent this by locking
**reference assets** up front and feeding them into every later generation.

## Why this works
Nano Banana 2 *edit* and Seedance *reference-to-video* are both reference-conditioned:
when you pass a clean reference image, they preserve it. So your job is to (a) create
one canonical image of each recurring element, (b) never generate that element from
scratch again — always pass the canonical reference in, and (c) **chain the scene** —
pass the *previous frame* in as a reference whenever a shot continues an established
scene, so the environment carries forward instead of being re-invented (see §D).

---

## A. Product plate (always)

The plate is the single source of truth for how the product looks.

1. Start from the user's product photo. Call `fal-ai/nano-banana-2/edit` with that
   photo in `image_urls`, prompt: "Clean studio hero shot of this exact product on a
   seamless [brand-color] background, soft commercial lighting, label fully legible,
   sharp focus. Keep the product identical to the reference." Generate `num_images: 3`
   and pick the cleanest.
2. Optionally make 2–3 plate variants (angles / on-brand backdrops) — but they must
   all read as the *same* object.
3. Record the plate URL/local path. Every keyframe edit passes the plate as a
   reference image, and you prompt "keep the product's label, shape, and color exactly
   as in the reference."

Never let a downstream prompt invent the product. If the product appears in a shot,
the plate goes into `image_urls`.

---

## B. Character sheet (when there's talent)

If the ad has a person, mascot, or recurring character, build a sheet so they look
identical in every shot. There are two starting points — handle them differently.

### B1. A real face was uploaded → preserve it exactly (highest priority)
When the brief centers on a specific real person (an uploaded photo of the founder, a
customer, a model), the goal is **fidelity to that exact face**, not a pretty
look-alike. Drifted or "beautified" faces are the most jarring failure of all.

1. **Treat the uploaded photo as the canonical face reference.** Save it locally; it
   goes into `image_urls` on *every* frame that shows this person.
2. **Build the multi-view sheet *from that photo*** with `fal-ai/nano-banana-2/edit`:
   "From the person in image 1, create a character sheet on a plain neutral background
   (front, 3/4, profile; neutral + smiling; full-body + close-up). **Preserve the exact
   face: same facial structure, eye shape and color, nose, mouth, eyebrows, jawline,
   skin tone, and proportions. Do not stylize, beautify, slim, or age the face.**"
   Generate `num_images: 3–4` and pick the truest likeness; if none match, re-roll —
   do not settle for "close."
3. **Carry the original photo forward, not just the sheet.** On each keyframe, pass
   *both* the original face photo and the sheet in `image_urls`, and restate the lock:
   "preserve the exact face from image 1 — identical features and proportions; do not
   change the identity." The original photo anchors identity better than a regenerated
   sheet alone.
4. **Verify likeness** on the storyboard before animating: put the original next to
   each keyframe and confirm it reads as the same person. Fix at the still stage — it is
   far cheaper than after animation.
5. ⚠️ If a Seedance reference call r