# Changelog

All notable changes to this skill pack. Format follows Keep a Changelog; versions use semantic versioning.

## [2.1.0] — 2026-11-11

### Added
- Split the monolithic skill into six installable skills: `motion-studio`, `blender-animation`, `remotion-motion-graphics`, `manim-animation`, `motion-design`, `video-composition`.
- `blender-animation`: headless `bpy` playbook, copy-ready recipes (data-API meshes, materials, type, particles, camera rigs, glare, batch render), runnable `scene_template.py`.
- `remotion-motion-graphics`: determinism rules, scene architecture, transitions, captions, data-driven compositions, starter components.
- `manim-animation`: isolated `uv` install, scene design, graph/ValueTracker patterns, 3D, algorithm visualization.
- `motion-design`: art-direction translation tables, timing/easing cookbooks, typography and RTL guidance, sound direction.
- `video-composition`: FFmpeg cookbook, loudness and ducking, subtitle burn-in, platform encodes, `validate.sh`.
- `motion-studio`: tool-selection matrix, installation audit, production pipeline, quality checklist, troubleshooting/security, project templates, `doctor.py`.
- One-command installer and cross-agent compatibility docs.

### Changed
- Frame math made explicit (Remotion 0-based vs Blender 1-based, inclusive end frames).
- Remotion licensing treated as a checkpoint with a link to current terms.
- Blender MCP documented as optional third-party, never a dependency.
- Quality gate requires visual inspection or an explicit statement that it did not happen.

## [2.0.0] — earlier

- Modular motion-studio package: playbooks for Blender, Remotion, production, design/sound, troubleshooting/security.

## [1.0.0] — earlier

- Initial single-file motion-studio skill.
