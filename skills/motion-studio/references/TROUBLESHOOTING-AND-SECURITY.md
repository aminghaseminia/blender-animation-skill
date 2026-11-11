# Troubleshooting, Safety, and Recovery

Reference for `motion-studio`. Fix causes, not symptoms.

## 1. Debugging protocol

1. Capture the complete error and the exact command.
2. Identify the layer: OS, dependency, package manager, API, asset, renderer, encoder, filesystem, integration.
3. Check the installed version's documentation.
4. Reproduce with the smallest possible scene/component/command.
5. Change one thing.
6. Run the smallest valid test.
7. Keep logs and the last known-good render.

Do not rerun an identical failing command. Do not "fix" by deleting user data, disabling security, or bulk-upgrading dependencies.

## 2. Blender

| Symptom | Cause | Fix |
|---|---|---|
| `blender: command not found` | Not on PATH | Use the full path; verify the install |
| `ModuleNotFoundError: bpy` | System Python | Run through `blender --background --python` |
| Operator context error | No valid area/selection | Prefer `bpy.data`; use `temp_override` if unavoidable |
| `AttributeError` on a property | API changed by version | Check `bpy.app.version`, inspect RNA, consult matching docs |
| Missing textures/fonts | Absolute/broken paths | `//relative` paths, pack, or ship assets |
| Render crash / OOM | Samples, geometry, textures, cache | Reduce one variable at a time; test CPU |
| Simulation differs between runs | Unbaked or external cache | Bake into the project, document it |
| Frames missing after a batch | Crash mid-range | Count files vs expected; rerender the gap |
| EEVEE/Cycles mismatch | Different pipelines | Test both engines; verify alpha and transparency |
| `.blend` will not open | Saved by a newer major version | Open with the newer build; restore backup |

## 3. Remotion / Node

| Symptom | Cause | Fix |
|---|---|---|
| Composition not found | Wrong entry or ID | `npx remotion compositions <entry>` |
| Blank render, fine preview | Asset path or font load | `staticFile`, correct `public/` casing, await fonts |
| Font fallback (Times) | Font not loaded | Load before render; confirm in a still |
| Render differs each time | Wall-clock/random state | Frame-derived state, seeded random |
| Slow or OOM | Concurrency, blur, DOM count | `--concurrency=4`, `--scale=0.5`, cache background |
| Audio drift | `startFrom`, fps, VFR source | Probe source; align in frames |
| Dependency breakage | Unpinned upgrades | Restore lockfile, `npm ci` |

## 4. FFmpeg

| Symptom | Cause | Fix |
|---|---|---|
| `Unknown encoder` | Build lacks it | `ffmpeg -encoders`, pick available |
| Concat garbage | Stream copy on mismatched inputs | Normalize, filter-concat |
| Alpha is black | MP4/H.264 | PNG sequence or ProRes 4444 |
| Audio out of sync | Sample rate/offset mismatch | `-ar 48000 -ac 2` everywhere |
| Colour shift | Metadata/view transform | Tag colour, compare still, avoid double conversion |
| Wrong duration | VFR / wrong `-framerate` | Normalize `fps=30`, verify count |

## 5. Security rules

- Treat generated code, npm packages, Blender add-ons, MCP servers, and downloaded assets as executable code. Review before use.
- Keep MCP/control servers on loopback. Never expose Blender's scripting interface to a network.
- No API keys or tokens in source, prompts, logs, or Git. Use environment variables.
- Do not upload private footage, unreleased product material, identity data, or confidential scripts to cloud services without explicit permission.
- Do not disable Gatekeeper, antivirus, browser protections, or code-signing checks to make a tool work.
- Avoid `sudo`/administrator steps unless necessary; explain why first.
- Prefer project-local installs to global ones.

## 6. Project hygiene

- Inspect folders before creating or overwriting files.
- Keep outputs inside the project unless told otherwise.
- Back up `.blend` files before major-version conversions.
- Keep secrets out of Git; `.env` in `.gitignore`.
- Commit source, config, scripts, lockfiles, and small assets — not multi-GB renders.
- Record asset sources and licences in `asset-manifest.md` or `project-manifest.json`.

## 7. Stop and ask before

- purchases, paid assets, paid cloud rendering;
- uploading private or client material to any external service;
- destructive overwrites, deletions, or major-version conversion of a project;
- broad system changes or elevated installs with unclear impact;
- using copyrighted material without clear authorization;
- a render likely to consume unusual time, storage, or compute.

Reversible, low-risk implementation choices are autonomous. These are not.

## 8. Recovery patterns

- **Corrupt render**: keep the image sequence; re-encode. If the sequence is bad, rerender only the affected range.
- **Broken composite**: rebuild the filter graph from normalized intermediates; do not try to patch the final file.
- **Regressed revision**: restore the last good render and source; reapply the change on a branch/copy.
- **Environment drift**: record versions at project start; recreate with the lockfile or pinned installer.

## 9. Reporting a failure

State: what failed, the exact command, the error excerpt, what you tried, what you changed, and what remains unverified. Do not claim success after a partial render.
