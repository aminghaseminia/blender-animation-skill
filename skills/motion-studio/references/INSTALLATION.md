# Installation and Environment Audit

Reference for `motion-studio`. Install only what the request needs, after inspecting the machine.

## 1. Policy

- Do not run a bulk installer on first contact.
- Reuse working installations. Never install a second copy of a tool that already works.
- Prefer official installers, official archives, or the OS package manager.
- Avoid `sudo pip`, global npm packages, unreviewed shell scripts, and `curl | sh` unless it is the vendor's documented method and you have inspected it.
- Do not modify shell profiles without need and permission.
- Record exact executable paths and versions in the project README.
- Explain elevated permissions, downloads > 100 MB, accounts, and paid services before proceeding.

## 2. Inventory first

```bash
python3 <skills-dir>/motion-studio/scripts/doctor.py
python3 <skills-dir>/motion-studio/scripts/doctor.py --json
python3 <skills-dir>/motion-studio/scripts/doctor.py --required blender,ffmpeg,node
```

Then inspect the relevant tools directly:

```bash
blender --version
node --version && npm --version
ffmpeg -version && ffprobe -version
uv --version
git --version
```

System context:

```bash
uname -a                 # macOS / Linux
cat /etc/os-release      # Linux
# Windows (PowerShell):
Get-ComputerInfo | Select-Object WindowsProductName, OsArchitecture
```

Check free disk before installing or rendering. A 4K EXR sequence can consume hundreds of GB.

```bash
df -h ~        # macOS/Linux
```

## 3. Blender

Official: https://www.blender.org/download/ — use a current stable/LTS build. Avoid beta/nightly for delivery unless a required feature demands it.

### macOS
```bash
brew install --cask blender
```
Or the official disk image matching Apple Silicon / Intel.

### Windows
```powershell
winget install --id BlenderFoundation.Blender -e
```
Or the official installer/portable archive. If `blender` is not on `PATH`, use the full path in the project config.

### Linux
```bash
sudo apt update
apt-cache policy blender        # check the version first
sudo apt install blender
```
If the distro package is too old for the required feature, use the official Linux archive. Do not add an unknown PPA.

### Verify the bundled Python
```bash
blender --background --factory-startup --python-expr \
  "import bpy, sys; print('Blender', bpy.app.version_string); print('Python', sys.version.split()[0]); print(sys.executable)"
```

`bpy` belongs to Blender's runtime. Do not `pip install bpy` and do not run scene scripts with the system interpreter.

## 4. Node.js and Remotion

Use a supported LTS (20 or 22 at time of writing; check https://nodejs.org).

### macOS
```bash
brew install node
```
### Windows
```powershell
winget install --id OpenJS.NodeJS.LTS -e
```
### Linux
Use the official NodeSource guidance or a version manager (fnm/nvm). Verify the version rather than assuming the distro package is current.

```bash
node --version
npm --version
```

Create a project and add Remotion's agent skills:

```bash
npx create-video@latest my-video      # choose the blank template
cd my-video
npx skills add remotion-dev/skills    # official Remotion agent skills
npm run dev
```

Commit the lockfile; use `npm ci` afterwards for reproducible installs. Update skills deliberately with the current upgrade guidance (`/remotion-upgrade` skill or `npx skills update`).

Docs: https://www.remotion.dev/docs/ · https://www.remotion.dev/docs/ai/skills

## 5. FFmpeg / FFprobe

### macOS
```bash
brew install ffmpeg
```
### Windows
```powershell
winget search ffmpeg    # inspect the publisher before installing
```
Or a reputable build linked from https://ffmpeg.org/download.html.

### Linux
```bash
sudo apt update
sudo apt install ffmpeg
```

Verify capabilities rather than assuming:

```bash
ffmpeg -version
ffmpeg -encoders | grep -E "libx264|libx265|prores|aac"
ffmpeg -filters  | grep -E "subtitles|overlay|loudnorm|sidechain"
ffprobe -version
```

Codec availability depends on how the build was configured; licensing can restrict some encoders.

## 6. Manim (optional)

Only for math/science/diagram work.

```bash
# install uv: https://docs.astral.sh/uv/getting-started/installation/
uv init --python 3.12 manim-project
cd manim-project
uv add manim
uv run manim --version
```

Linux native dependencies:

```bash
sudo apt install build-essential python3-dev pkg-config libcairo2-dev libpango1.0-dev ffmpeg
sudo apt install texlive texlive-latex-extra texlive-fonts-recommended
```

macOS: `brew install cairo pango pkg-config ffmpeg` plus a TeX distribution for `MathTex`.
Windows: FFmpeg + MiKTeX/TeX Live; Microsoft C++ Build Tools may be required.

Docs: https://docs.manim.community/en/stable/installation.html

## 7. Installing this skill pack

Canonical layout: one directory per skill, all siblings:

```text
<skills-dir>/
  motion-studio/
  blender-animation/
  remotion-motion-graphics/
  manim-animation/
  motion-design/
  video-composition/
```

Common locations:

| Agent | Global | Project |
|---|---|---|
| OpenCode | `~/.config/opencode/skills/` | `<project>/.opencode/skills/` |
| Generic / agents.md | `~/.agents/skills/` | `<project>/.agents/skills/` |
| Claude Code | `~/.claude/skills/` | `<project>/.claude/skills/` |

Install with the repo's script (copies every skill):

```bash
./install.sh --target ~/.config/opencode/skills
```

Or manually:

```bash
mkdir -p ~/.config/opencode/skills
cp -R skills/* ~/.config/opencode/skills/
```

Do not install the same skill ID in multiple locations unless you understand the agent's precedence rules.

## 8. Optional Blender MCP

Scripts in background mode are the production path: reproducible, diffable, CI-friendly. MCP is useful for interactive inspection of an already-open session.

Third-party project: https://github.com/ahujasid/mcp-for-blender (formerly `blender-mcp`). It is not an official Blender component.

Before installing:

1. Read the current repository, licence, and setup instructions.
2. Verify compatibility with the installed Blender and agent client.
3. Understand that its tools can execute arbitrary Python inside Blender.
4. Review telemetry options and disable them if desired.
5. Keep the server on loopback. Never expose it to an untrusted network — the project documents no authentication/encryption for remote access.
6. Do not paste credentials into source files or chat logs; use environment variables.

Never make MCP a dependency of a delivered project.

## 9. Verification after install

```bash
blender --version
node --version
ffmpeg -version | head -1
ffprobe -version | head -1
python3 <skills-dir>/motion-studio/scripts/doctor.py
```

Run one tiny end-to-end test per engine before starting a real project:

- Blender: build a cube, render one frame, confirm a non-zero PNG.
- Remotion: render a 2-second composition at 50% scale.
- FFmpeg: encode 2 seconds of testsrc and probe it.

A pipeline that has never rendered a test frame is not verified.
