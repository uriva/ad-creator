# Prompting Guide — Nano Banana 2 & Seedance 2.0

Distilled from Google's official Nano Banana prompting guide and ByteDance's official
Seedance 2.0 prompt guide, adapted for ad production. The two models want **different**
prompt styles — don't use the same prompt for both.

> One sentence to remember: **stills are written like a photographer/creative
> director; motion is written like a director talking to an editor.**

## Table of contents
1. Nano Banana 2 — core principles
2. Nano Banana 2 — the five frameworks (generate, multimodal, edit, text, director)
3. Nano Banana 2 — creative-director controls (light / lens / grade / material)
4. Seedance 2.0 — the 6-step formula
5. Seedance 2.0 — camera movement rules (the 8 moves + pacing)
6. Seedance 2.0 — image-to-video & reference-to-video specifics
7. Seedance 2.0 — negative prompts & danger words
8. Iteration: change one variable
9. Worked ad examples

See `cinematography.md` for the underlying directing/composition vocabulary that
feeds both.

---

## 1. Nano Banana 2 — core principles
- **Describe the scene narratively; don't stack keywords.** A descriptive sentence or
  paragraph beats a comma-salad of tags. The model reasons over the whole brief.
- **Front-load what matters.** List details most-important first — earlier words carry
  more weight. Lead with the operation verb ("Create…", "Place…", "Replace…").
- **Be specific & concrete.** "navy blue tweed jacket," not "jacket." "ornate ceramic
  jar," not "container." Materiality and exact nouns drive realism.
- **Use positive framing.** Say what you want, not what you don't: "an empty street,"
  not "a street with no cars."
- **State the aspect ratio** when it matters (the model supports 1:1, 3:2, 2:3, 3:4,
  4:3, 4:5, 5:4, 9:16, 16:9, 21:9, plus extremes). We also pass it as the
  `aspect_ratio` param — do both for reliability.
- **Iterate conversationally.** Refine with follow-up edits rather than rewriting from
  scratch.

## 2. Nano Banana 2 — the five frameworks

**(a) Text-to-image (no reference).** You're the director of a blank canvas.
Formula: `[Subject] + [Action] + [Location/Context] + [Composition] + [Style]`
> "A striking fashion model in a tailored brown dress and structured handbag, posing
> with a confident statuesque stance slightly turned, against a seamless deep-cherry
> studio backdrop, medium-full shot center-framed, editorial fashion-magazine style
> shot on medium-format film with pronounced grain and cinematic lighting."

**(b) Multimodal (with references) — the consistency workhorse for `edit`.**
Formula: `[Reference images] + [Relationship instruction] + [New scenario]`
> "Using the product in image 1 and the woman in image 2: place her holding the
> product on a sunlit balcony at golden hour. Keep the product's label and her face
> exactly as the references."
Up to many reference images can be combined; this is how you merge a real product into
a new scene and hold character identity. **For scene continuity, also pass the previous
keyframe as one of the references** and instruct the model to continue that exact
environment: "Continue the scene in image 3 (same set, lighting, props, wardrobe, time
of day); same character and product as images 1–2; now a [shot size/angle] of [next
beat]." Each continuing frame should see the frame it continues from.

**(c) Editing an existing image.** Focus on *what changes* and *what stays the same*.
Be explicit about preservation: "Remove the man on the left; keep everything else
identical." Text-defined masks (inpainting) work — name the region in words.

**(d) Text rendering.** Nano Banana 2 renders sharp text — useful for end cards.
- Put the exact copy in **quotes**: `the words "FEEL THE GLOW"`.
- Name the typography: "bold white sans-serif," "elegant brush script."
- Text-first hack: settle the wording in conversation first, then ask for the image.
- Still prefer adding final marketing copy as real vector/text in the edit for max
  legibility (see `editing.md`); generated text is great for layout/comps.

**(e) Real-world grounding (web search).** With `enable_web_search: true` the model can
look up how a real place/object/logo actually looks before drawing it. Use for real
landmarks, real product categories, or current/localized references.

## 3. Nano Banana 2 — creative-director controls
Layer these four on top of any framework; this is what turns "good" into "broadcast."

- **Lighting** (highest visual leverage): "three-point softbox setup," "chiaroscuro,
  harsh high contrast," "golden-hour backlight with long shadows," "soft radiant
  studio light."
- **Camera / lens / hardware**: dictate perspective and the visual DNA. "low-angle,
  shallow depth of field (f/1.8)," "85mm portrait lens," "wide-angle for scale,"
  "macro for detail." Naming a device shifts the look: "shot on Fujifilm" (color
  science), "GoPro" (i