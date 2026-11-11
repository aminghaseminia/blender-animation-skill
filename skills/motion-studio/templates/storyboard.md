# Storyboard — {{PROJECT}}

FPS: `30` · Master: `1920×1080` · Total: `___ s = ___ frames`

| # | Scene | Start | End | Frames |
|---|---|---|---|---|
| 01 | | 0.0 s | 3.0 s | 0–89 |
| 02 | | 3.0 s | 9.0 s | 90–269 |
| 03 | | 9.0 s | 12.0 s | 270–359 |

> Remotion indices are 0-based. Blender frames are 1-based. Keep one mapping for the whole project.

---

## Scene 01 — {{NAME}}

```text
Time         00:00.0 – 00:03.0   (frames 0–89)
Purpose      what this scene must accomplish
Composition  framing, focal point, negative space
Copy         exact on-screen text
Elements     objects / graphics / footage
Motion       entrances, exits, easing, stagger
Camera       none / dolly / orbit / zoom (with intent)
Transition   in: cut  |  out: 8 f crossfade
Sound        cue and timing
Tool         Remotion / Blender / Manim
Output       MP4 / PNG sequence with alpha
QA           what could go wrong here, and how you will check
```

Style frame: `previews/style-01.png`

---

## Scene 02 — {{NAME}}

```text
Time
Purpose
Composition
Copy
Elements
Motion
Camera
Transition
Sound
Tool
Output
QA
```

Style frame: `previews/style-02.png`

---

## Scene 03 — {{NAME}}

```text
Time
Purpose
Composition
Copy
Elements
Motion
Camera
Transition
Sound
Tool
Output
QA
```

---

## Audio map

| Time | Event | Stem | Notes |
|---|---|---|---|
| 0.0 | bed starts | music | fade in 1 s |
| 3.0 | transition whoosh | sfx | align to cut |
| 7.0 | logo impact | sfx | -6 dB under voice |
| 12.0 | fade out | music | 1.5 s |

## Delivery map

| File | Size | FPS | Purpose |
|---|---|---|---|
| output/final.mp4 | 1920×1080 | 30 | primary |
| output/final_vertical.mp4 | 1080×1920 | 30 | social |
