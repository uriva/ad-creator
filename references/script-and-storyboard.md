# Script, Shot List & Storyboard

## 30-second pacing math
A commercial is a sequence of short shots, not one long take. Seedance clips run
4–15s; you'll cut several together.

| Target | Shots | Typical shot length | Structure |
|---|---|---|---|
| 6s | 2–3 | 2–3s | Hook → product → logo |
| 15s | 3–5 | 3–4s | Hook → benefit → product hero → CTA/logo |
| 30s | 5–8 | 3–6s | Hook → problem → benefit beats → product hero → CTA → end card |

Rules of thumb: a shot under ~2s reads as a flash; over ~6s drags unless it's a hero
beat. Open with a 1–2s hook. Always end on a product + logo/CTA card (~2–3s).

## Script template (output this in chat)

```
TITLE: <ad name>   |   DURATION: <Ns>   |   ASPECT: <16:9 / 9:16 / 1:1>
TONE: <...>   |   MESSAGE: <one line>   |   CTA: <...>

| # | Dur | Shot (size + action, on screen)        | Camera        | On-screen text | Audio / VO / SFX        |
|---|-----|----------------------------------------|---------------|----------------|-------------------------|
| 1 | 2s  | CU product backlit on dark surface     | slow push-in  | —              | rising whoosh           |
| 2 | 4s  | MED woman uses product, smiles         | handheld      | "Feel it"      | VO + soft music         |
| 3 | 4s  | WIDE lifestyle, product in hand        | dolly left    | —              | music swells            |
| 4 | 3s  | CU product hero, label readable        | locked-off    | brand line     | SFX ping                |
| 5 | 2s  | END CARD: logo + tagline + CTA         | static        | tagline + CTA  | music button-out        |
|   | 15s | TOTAL                                  |               |                |                         |
```

Make the durations sum to the target. Note which shots need talent (→ character
sheet) and which need an end-frame (→ Seedance `end_image_url`).

## From script to storyboard (Stage 3)
For each row, design **one hero keyframe** (the most important frame of the shot) with
`fal-ai/nano-banana-2/edit`, passing the product plate (+ character sheet) as
references and matching the locked aspect ratio and grade. For shots with a defined
motion destination, also design the **end frame**.

Then build a contact sheet with `scripts/build_contact_sheet.py`:
```
python scripts/build_contact_sheet.py --frames f1.png f2.png ... \
  --labels "1 · 2s · CU product" "2 · 4s · woman uses product" ... \
  --out storyboard.png --cols 3
```

## The approval gate (mandatory)
Present the storyboard and stop. Suggested message:

> "Here's the storyboard — one hero frame per shot, with durations. Check the product
> look, the character, the framing, and the flow. Tell me what to change, or approve
> and I'll animate. I hold off on video until you approve because animation is the
> slow, billed step."

Iterate keyframes (cheap) until approved. Only then go to Stage 4. Capture the
approved frame → shot mapping (paths, durations, which model, audio on/off, end-frame)
in a small `shots.json` so the animation and edit stages stay organized.
