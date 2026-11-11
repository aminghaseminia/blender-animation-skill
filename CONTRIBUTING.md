# Contributing

Thanks for improving the pack. Keep contributions **vendor-neutral**, **tool-honest**, and **project-agnostic**.

## What belongs here

- A new engine playbook (e.g. Three.js, Rive, Cavalry, Natron) as a sibling skill.
- New, tested recipes for Blender/Remotion/Manim/FFmpeg.
- Better quality checks, failure tables, and validation scripts.
- Fixes for API drift after a Blender/Remotion/Manim release.
- Translations of skill descriptions (keep the English source authoritative).

## What does not

- Project-specific assets, brand material, or client work.
- "Magic prompt" collections that produce unreviewable output.
- Claims that a render is correct without a verification path.
- Bulk-install scripts that touch a user's system without an audit.
- Unlicensed fonts, music, models, or reference files.

## Skill format

Each skill lives at `skills/<name>/SKILL.md` with YAML frontmatter:

```yaml
---
name: <must match the directory>
description: <what it does + when to use it; include trigger phrases>
compatibility: <runtime/tool requirements>
metadata:
  domain: <domain>
  version: <semver>
license: MIT
---
```

Rules:

- `name` must be lowercase, hyphenated, and equal to the folder name.
- `description` starts with the capability, then the triggers ("Use when…"). This is what routing relies on.
- Long material goes in `references/`, not in `SKILL.md`. `SKILL.md` should stay under ~500 lines.
- Relative links must resolve inside the skill folder.
- Code samples must be runnable or clearly marked as illustrative.
- Do not claim an API detail you have not checked against the current docs.

## Verify before opening a PR

```bash
python3 scripts/validate_skills.py
bash -n install.sh
for f in skills/*/scripts/*.sh; do bash -n "$f"; done
python3 -m compileall -q skills
```

If you changed a recipe, run it against the real tool when possible, and note the version you tested (`Blender 4.5.3`, `Remotion 4.0.x`, `FFmpeg 8.0.1`).

## Commit style

```
skill(blender-animation): add Geometry Nodes scatter recipe
fix(video-composition): correct concat example for mismatched fps
docs: clarify Remotion licensing checkpoint
```

## Review criteria

1. Would an agent make a **better decision** after reading this?
2. Is the failure mode covered, not just the happy path?
3. Is it reproducible and free of assumptions about the user's machine?
4. Does it preserve the user's files and licences?

If yes to all four, it belongs in the pack.
