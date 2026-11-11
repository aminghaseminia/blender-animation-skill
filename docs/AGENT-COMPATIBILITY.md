# Agent Compatibility

The pack uses the plain [Agent Skills](https://opencode.ai/docs/skills/) layout: a folder with `SKILL.md` plus optional `references/`, `scripts/`, and `templates/`. No proprietary runtime, no server.

## Requirements

| Capability | Required? | Effect |
|---|---|---|
| Filesystem read | Yes | Load `SKILL.md` and references |
| Shell execution | Yes | Run Blender, Node, FFmpeg |
| Image viewing (vision) | Strongly recommended | Inspect rendered frames |
| Subagents / parallel tasks | Optional | Render or build scenes concurrently |
| Network | Optional | Package installs, docs lookup |

Without vision, the agent can still build and technically validate, but it must report that visual QA is incomplete. The skills enforce that honesty.

## Install locations

| Agent | Global | Project-local | Invocation |
|---|---|---|---|
| **OpenCode** | `~/.config/opencode/skills/<name>/` | `.opencode/skills/<name>/` | `@<skill-name>` or a matching request |
| **Claude Code** | `~/.claude/skills/<name>/` | `.claude/skills/<name>/` | `/skills` then request, or mention the skill |
| **Codex CLI** | `~/.agents/skills/<name>/` | `.agents/skills/<name>/` | request; reads `AGENTS.md` |
| **Cursor** | tool-specific | `.cursor/rules/` or `AGENTS.md` | reference the skill file explicitly |
| **Gemini CLI** | `~/.gemini/skills/` (if supported) | project `.gemini/` | request |
| **Any agent** | a folder it can read | same | "Read `skills/blender-animation/SKILL.md` and follow it" |

If your agent has no native skills support, add one line to `AGENTS.md`:

```markdown
## Animation
For any animation, video, motion-graphics, Blender, Remotion, Manim, or FFmpeg task,
read `skills/motion-studio/SKILL.md` first, then the skill it routes to.
```

That single instruction is enough for most agents, because `motion-studio` contains the routing logic.

## Why sibling installation matters

`motion-studio` delegates to the other five by relative path (`../blender-animation/SKILL.md`). Installing only `motion-studio` gives you the orchestration logic but not the engine playbooks. Install the full pack unless you deliberately want one engine:

```bash
./install.sh --target ~/.config/opencode/skills blender-animation
```

## Behaviour differences to expect

- **Agents with vision** inspect frames and iterate; expect 2–4 revision loops on a real project.
- **Text-only agents** verify specs, validate files, and hand you a residual visual checklist. They should not claim a video "looks good".
- **Agents with subagents** may split scenes across workers; keep the frame map in `storyboard.md` as the shared contract.
- **Agents with long context** can read all references at once; others should load only the skill and playbook for the current engine.

## Tool availability

The agent audits first. A missing engine is not a failure; it changes the plan:

| Available | Sensible plan |
|---|---|
| Blender + FFmpeg | 3D scenes, titles rendered as 3D type, FFmpeg assembly |
| Node + FFmpeg | Remotion-first motion graphics |
| FFmpeg only | Assembly, captions, audio, format delivery — no generated animation |
| Nothing | Report the gap and the exact install steps; do not fake renders |

## Security notes for MCP-enabled agents

If the agent can attach MCP servers, treat Blender/MCP integrations as code execution:

- loopback only, no public exposure;
- review the server before enabling;
- no credentials in prompts or project files;
- prefer plain scripts for delivered work, so the project remains reproducible without the MCP session.
