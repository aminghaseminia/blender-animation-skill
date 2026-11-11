# Agent Instructions

This repository is an **agent skill pack** for animation and motion graphics.

## If you are an AI agent working in this repo

- To use the skills, read `skills/motion-studio/SKILL.md` first. It routes to:
  - `skills/blender-animation/SKILL.md` — 3D with Blender Python
  - `skills/remotion-motion-graphics/SKILL.md` — 2D/React video
  - `skills/manim-animation/SKILL.md` — math/science animation
  - `skills/motion-design/SKILL.md` — art direction and motion craft
  - `skills/video-composition/SKILL.md` — FFmpeg assembly and validation
- Install the pack with `./install.sh` (see README) rather than copying files ad hoc.
- Do not modify another user's installed skills without a backup.
- Before claiming a render is correct, inspect actual frames or state clearly what was not verified.

## If you are contributing

Follow `CONTRIBUTING.md`. Validate with:

```bash
python3 scripts/validate_skills.py
python3 -m compileall -q skills scripts
bash -n install.sh
```

## Project conventions

- Source over output: the build script and editable project are deliverables.
- Determinism: frame-derived animation, seeded randomness, no wall-clock timing.
- One frame map: Remotion 0-based indices, Blender 1-based inclusive frames.
- Never commit renders, caches, `node_modules`, or secrets.
