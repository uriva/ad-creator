# Directing & Composition — Shot Grammar for Ads

This is the visual vocabulary that feeds both the still prompts (Nano Banana 2) and
the motion prompts (Seedance). You direct the AI the way a DP and director would
direct a crew: shot size, composition, lighting, lens, camera move, and continuity.
Use these terms explicitly in prompts — both models respond to them.

## Table of contents
1. Shot sizes (the building blocks)
2. Composition rules
3. Camera angles
4. Camera moves and what they *mean*
5. Lighting setups
6. Lens & depth language
7. Continuity & editing grammar (so the cut works)
8. A shot-design checklist per keyframe

---

## 1. Shot sizes
Pick the size for each shot by what the viewer must feel/read:
- **Extreme close-up (ECU):** a detail — texture, a logo, an eye. Intimacy, emphasis.
- **Close-up (CU):** face or product filling the frame. Emotion, the hero beat.
- **Medium close-up (MCU):** head-and-shoulders. Dialogue, connection.
- **Medium (MS):** waist up. Natural, conversational.
- **Medium-wide / cowboy:** knees up. Body language + some context.
- **Wide (WS):** full body in setting. Lifestyle, action, scale.
- **Extreme wide / establishing (EWS):** the world. Sets place and scale.

Ad rhythm: cut between sizes. A spot that stays one size feels flat. Classic beat
order: wide to orient → medium for the human → close for emotion → ECU on the product.

## 2. Composition rules
- **Rule of thirds:** place key subjects on the third-lines / their intersections, not
  dead center, for natural balance. (Centered/symmetry is a deliberate alternate look.)
- **Leading lines:** use lines in the scene (roads, edges, light) to point the eye to
  the product.
- **Framing (frame-within-a-frame):** doorways, windows, foreground objects to focus
  attention and add depth.
- **Headroom & lead room (nose/look room):** leave appropriate space above the head and
  in the direction a subject looks or moves — too little feels cramped, too much feels
  empty.
- **Negative space:** intentional empty area — elegant, premium, and **leaves room for
  on-screen text and logos** (ask for it in keyframes).
- **Balance & depth:** distribute visual weight; build foreground / midground /
  background layers so the frame reads three-dimensional.

## 3. Camera angles
- **Eye-level:** neutral, relatable.
- **Low angle:** subject/product looks powerful, heroic, aspirational.
- **High angle:** subject looks smaller/vulnerable; good for overviews.
- **Overhead / top-down:** great for flat-lay product and food.
- **Dutch tilt:** tension/energy — use sparingly.

## 4. Camera moves and what they *mean*
Motion is emotional punctuation, not decoration. Match move to intent (and obey the
Seedance "one primary move" rule):
- **Push-in (dolly in):** intensify, draw into emotion or onto the product. The default
  hero move.
- **Pull-out:** reveal context, end a thought, breathe.
- **Tracking / follow:** stay with a moving subject — energy, momentum.
- **Pan / tilt:** scan a space or connect two elements.
- **Orbit / arc:** show a product in the round; premium, dimensional.
- **Crane up/down:** scale, grandeur, or settling down into a scene.
- **Handheld:** authenticity, urgency, documentary realism.
- **Locked-off:** stillness lets the subject's action or a snappy cut carry the energy.
Pace words: slow / smooth / gentle / gradual read as premium; "fast" reads as chaos —
reserve speed for one element only.

## 5. Lighting setups
Lighting is the highest-leverage choice for mood and perceived quality.
- **Three-point (key + fill + back/rim):** clean, controlled, the studio default.
- **High-key:** bright, low-contrast, optimistic, clean (beauty, tech, food).
- **Low-key / chiaroscuro:** dark, high-contrast, dramatic, premium, moody.
- **Golden hour / backlight:** warm, aspirational, lifestyle.
- **Rim/edge light:** separates subject from a dark background — makes product pop.
- **Practical / neon:** in-scene light sources; modern, urban, energetic.
- **Soft window / overcast:** gentle, natural, honest.
Name the look and **reuse the same lighting words across every shot** for unity.

## 6. Lens & depth language
- **Wide (≈24–35mm):** scale, environment, slight drama; watch edge distortion.
- **Normal (≈50mm):** natural, human perspective.
- **Portrait/tele (≈85mm):** flattering compression, creamy bokeh — beauty & product.
- **Macro:** texture and tiny detail — labels, fabric, droplets.
- **Depth of field:** shallow (f/1.4–2.8) isolates the hero with soft background; deep
  (f/8–16) keeps the whole scene sharp. For stills, naming the f-stop steers the look;
  for Seedance, describe it as "shallow depth of field," not "f/1.8."

## 7. Continuity & editing grammar (so the cut works)
Plan the cut while you storyboard, not after:
- **180-degree rule / screen direction:** keep the camera on one side of the action
  line so subjects keep consistent left/right placement across shots — otherwise the
  edit feels disorienting. Design adjacent keyframes with consistent screen direction.
- **Eyeline & looking room:** if a subject looks frame-right in one shot, the thing
  they look at should pay off consistently.
- **Match on action / size jumps:** cut on a movement, and change shot size or angle
  enough between adjacent shots (the "30-degree" idea) so cuts feel intentional, not
  like a jump cut.
- **Motion continuity:** a push-in can hand off to a matching push-in; opposing moves
  on a hard cut feel jarring unless intended.
- **J/L cuts (audio):** let audio lead or trail a picture cut for a smooth, pro feel —
  apply in the edit (see `editing.md`).

## 8. Per-keyframe shot-design checklist
For each storyboard frame, decide and write into the prompt:
- [ ] Shot size and angle (and why — what should the viewer feel?)
- [ ] Composition (thirds/lead room/negative space for text)
- [ ] Lighting setup (same vocabulary as the rest of the spot)
- [ ] Lens/depth (hero isolation vs. context)
- [ ] Product hero placement + label legibility
- [ ] Screen direction consistent with neighboring shots (180° rule)
- [ ] The single camera move it will get in animation (Stage 4)
