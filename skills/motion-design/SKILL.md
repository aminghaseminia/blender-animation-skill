---
name: motion-design
description: Art direction and motion-design craft for animation projects — creative briefs, storyboards, style frames, colour and type systems, composition, timing and easing, transition vocabulary, sound direction, accessibility, and right-to-left (Persian/Arabic) typography. Use before building scenes, when a video looks amateur or generic, when choosing palette and fonts, when a request says "make it feel premium/cinematic/modern", or when text, rhythm, or hierarchy is not landing. Tool-agnostic; pairs with blender-animation, remotion-motion-graphics, and manim-animation.
compatibility: No runtime required. Applies to any animation tool or renderer.
metadata:
  domain: motion-design
  version: "2.1.0"
  role: craft
license: MIT
---

# Motion Design — Art Direction and Motion Craft

This skill turns adjectives into observable decisions. "Premium" is not gold gradients; it is restraint, spacing, controlled contrast, and considered timing. "Futuristic" is not random neon; it is a coherent grid, precise motion, and a limited palette.

Read `references/MOTION-CRAFT.md` for numbers, tables, and worked examples.

## 1. Start with a compact creative direction

Write these seven lines before any scene code:

```text
Subject:      one sentence
Audience:     who and where they watch
Message:      the one thing they must remember
Tone:         3 adjectives, each translated into a visual decision
Palette:      4–6 hex values with roles
Type:         1–2 families, weights, scale
Motion:       speed, easing character, transition vocabulary
```

If the tone adjectives cannot be translated into decisions, the direction is not finished. Example translation:

| Adjective | Concrete decisions |
|---|---|
| Premium | Slow easing, wide tracking on display type, 1 accent colour, deep negative space, soft key light, no bounce |
| Energetic | Fast entrances (8–12 frames), 6–10% overshoot, cut-on-beat, high contrast, saturated accent |
| Trustworthy | Symmetric grid, mid-tone palette, slow reveals, stable camera, plain language, no gimmicks |
| Technical | Monospace accents, ruled lines, measurement ticks, precise linear motion, cool neutrals |

## 2. One system, then scenes

Define the system once and reuse it:

- **Grid:** 12 columns, 5–8% outer margin. Vertical/social formats need more margin because platform UI covers edges.
- **Type scale:** e.g. 96/64/40/28/20 px at 1080p. Never invent a size per scene.
- **Spacing:** 8 px base unit. Space communicates grouping more than lines or boxes do.
- **Colour roles:** background, surface, primary text, muted text, accent, semantic. One accent, used sparingly.
- **Shape language:** corner radius, stroke weight, and whether elements are flat, bevelled, or lit.
- **Motion language:** entrance style, exit style, transition vocabulary, and whether camera moves exist at all.

A style frame is cheaper than ten finished scenes. Render one frame that represents the whole piece and get it right first.

## 3. Composition rules that hold up

- One focal point per beat. If two things are equally bright, equally large, and equally moving, there is no hierarchy.
- Contrast is relative: if everything glows, nothing does.
- Negative space is a feature. A 30% empty frame reads as confidence.
- Align to something — a grid, an optical centre, or a deliberate diagonal. Near-alignment looks like a mistake.
- Keep the subject out of the outer 5% on social formats.
- For text over imagery, ensure a luminance difference of at least ~4.5:1 for body copy; add a scrim rather than a heavy shadow.
- Depth cues in 2D: scale, blur, opacity, overlap, parallax. Use one or two, not all four.

## 4. Timing

Duration communicates weight. Rough starting points at 30 FPS:

| Element | Entrance | Exit | Dwell |
|---|---|---|---|
| Short headline (1–3 words) | 12–18 f | 8–12 f | ≥ 24 f |
| Long headline | 18–24 f | 12 f | ≥ 45 f |
| Body line | 12–16 f | 8 f | ≥ 30 f |
| Logo reveal | 24–40 f | 12 f | ≥ 45 f |
| Chart | 30–45 f | 10 f | ≥ 60 f |
| Full-screen transition | 10–18 f | — | — |
| Camera move (3D) | 45–90 f | — | — |

Rules:

- Bigger distance or mass → longer duration.
- Groups move together, then stagger by 2–6 frames; do not stagger everything by the same amount.
- Leave a beat of stillness after an important reveal.
- If a viewer must read it, it must be on screen about twice as long as you think.

## 5. Easing

| Situation | Curve |
|---|---|
| Arriving and settling | ease-out (cubic or quart) |
| Leaving | ease-in |
| Moving between two rest states | ease-in-out |
| Mechanical / continuous / looping | linear |
| Physical snap | spring, damping 14–22, stiffness 90–180 |
| Camera | very soft ease-in-out, long duration |

Never ease every property identically. Position, opacity, and rotation can share a curve; scale usually wants slightly tighter timing. Avoid bounce unless the brand is playful — it dates quickly and fights legibility.

## 6. Transitions

Build a vocabulary of 3–4 and reuse them:

1. **Cut** — default for pace. Cheapest and often best.
2. **Crossfade** — 6–12 frames, for soft continuity.
3. **Mask wipe** — directional, for a spatial relationship.
4. **Scale-through** — pushing into an element, for a chapter change.
5. **Match cut** — shape or motion continuity, the most satisfying and hardest.

Avoid: default zoom-blur on everything, star wipes, and transitions that contradict the story's direction of travel.

## 7. Colour

- Start from one dominant, one accent, and neutrals. Add a second accent only if it carries meaning.
- Check contrast at final size, not on a large monitor.
- Keep saturation controlled: highly saturated colours on large areas fatigue the eye.
- Dark backgrounds need slightly desaturated accents and lifted shadow detail; pure black plus pure white text is harsh.
- Use colour to encode meaning consistently (one colour for "before", another for "after"), not decoratively.
- Verify colour across tools: browser (sRGB), Blender (view transform), and encoder. A washed-out composite usually means mismatched view transforms, not a bad palette.

## 8. Typography

- Max two families: one display, one text (or one family with multiple weights).
- Display tracking: tight for large sans (-1% to -3%), wide for short all-caps labels (+8% to +20%).
- Body line height: 1.35–1.6. Display line height: 1.0–1.2.
- Line length: 45–75 characters. Headlines can be shorter.
- Avoid orphans and single-word last lines; rewrite the copy if needed.
- Numbers: tabular figures for counters and tables.
- Never stretch or condense a typeface to fit; change the layout or the size.

### Right-to-left (Persian, Arabic, Hebrew)

- Set direction at the container level and use a shaping-capable font (e.g. Vazirmatn, IBM Plex Sans Arabic, Noto Naskh Arabic).
- Test shaping, joining, diacritics, and punctuation in a **rendered frame**, not in code.
- Mixed content: keep Latin brand names/URLs in their own spans with `dir="ltr"`, or the bidi algorithm will reorder punctuation.
- Persian numerals vs Latin numerals: choose one system for the whole piece.
- Line height needs more room than Latin for the same optical size.
- Do not letter-space Arabic script — it breaks cursive joining.

## 9. Sound

- Decide the role of sound before choosing tracks: pace-setter, emotional bed, information (voice), or punctuation (SFX).
- Separate stems: voice, music, ambience, spot effects. Duck music 6–10 dB under voice.
- Accent the visual event, not the clip start.
- Fade every cut; a hard start or stop clicks.
- Leave headroom (-1 dBTP), avoid clipping, check mono compatibility for phone speakers.
- Silence is a tool. Dropping music for one beat before a reveal is stronger than adding a riser.
- License every track and record the source. Never assume "free download" means commercial use is allowed.

## 10. Accessibility and platform fit

- Captions for any spoken content; on-screen text also helps silent viewing, which is the majority on social.
- Do not encode meaning in colour alone.
- Avoid flashing above 3 Hz; no strobing.
- Keep essential text inside safe areas, at a size readable on a phone.
- Check the platform's current duration, aspect, codec, and bitrate requirements before delivery.

## 11. Review method

Watch the piece three times:

1. **Silent, at 50% size** — does the hierarchy read? Is anything clipped?
2. **Full size with sound** — does the rhythm work? Is the audio fighting the image?
3. **Frame by frame at boundaries** — flashes, gaps, jumps, unreadable frames.

Then ask the three questions:

- What is the one thing the viewer remembers?
- Where does attention go first, and is that intended?
- What can be removed without losing the message?

Removal is usually the highest-value revision.

## 12. Deliverable for the design phase

- `brief.md` — subject, audience, message, constraints, assumptions.
- `style-guide.md` — palette with roles and hex, type scale, spacing, motion language.
- `storyboard.md` — one row/block per scene: time, purpose, composition, copy, motion, transition, sound, tool.
- 1–3 style frames — the visual target, approved before mass production.
