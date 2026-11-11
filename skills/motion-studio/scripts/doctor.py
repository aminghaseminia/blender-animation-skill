#!/usr/bin/env python3
"""Motion Studio environment doctor.

Read-only inventory of the tools this skill pack can use. It never installs,
modifies, or uploads anything.

Usage:
    python3 doctor.py             # human-readable report
    python3 doctor.py --json      # machine-readable JSON
    python3 doctor.py --required blender,ffmpeg,node

Exit codes:
    0  all required tools found (or none requested)
    1  one or more required tools missing
"""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path

TOOLS = {
    "blender": ["--version"],
    "ffmpeg": ["-version"],
    "ffprobe": ["-version"],
    "node": ["--version"],
    "npm": ["--version"],
    "npx": ["--version"],
    "python3": ["--version"],
    "uv": ["--version"],
    "manim": ["--version"],
    "git": ["--version"],
    "magick": ["-version"],
    "convert": ["-version"],
    "nvidia-smi": ["--query-gpu=name,memory.total", "--format=csv,noheader"],
}

INTERPRETERS = ["python", "python3", "py"]


def run(cmd: list[str], timeout: int = 8) -> tuple[bool, str]:
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        return False, ""
    out = (proc.stdout or "").strip() or (proc.stderr or "").strip()
    first = out.splitlines()[0].strip() if out else ""
    return proc.returncode == 0 or bool(out), first


def find_tool(name: str) -> str | None:
    path = shutil.which(name)
    if path:
        return path
    # Windows / app bundles sometimes live outside PATH
    candidates = [
        Path("/Applications/Blender.app/Contents/MacOS/Blender"),
        Path("/snap/bin/blender"),
        Path.home() / "Applications" / "Blender.app" / "Contents" / "MacOS" / "Blender",
        Path("C:/Program Files/Blender Foundation/Blender 4.5/blender.exe"),
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return None


def python_info() -> dict:
    return {
        "executable": sys.executable,
        "version": sys.version.split()[0],
        "platform": platform.platform(),
        "machine": platform.machine(),
    }


def disk_free(path: Path) -> str:
    try:
        usage = shutil.disk_usage(path)
        return f"{usage.free / (1024 ** 3):.1f} GiB free of {usage.total / (1024 ** 3):.1f} GiB"
    except OSError:
        return "unknown"


def collect() -> dict:
    tools: dict[str, dict] = {}
    for name, args in TOOLS.items():
        path = find_tool(name)
        if not path:
            tools[name] = {"found": False, "path": None, "version": None}
            continue
        ok, version = run([path, *args])
        tools[name] = {"found": True, "path": path, "version": version if ok else None}

    # Blender's bundled Python (the one that can import bpy)
    blender = tools.get("blender", {})
    blender_python = None
    if blender.get("found"):
        expr = (
            "import sys; print(sys.version.split()[0]); "
            "print(sys.executable)"
        )
        ok, _ = True, ""
        try:
            proc = subprocess.run(
                [blender["path"], "--background", "--factory-startup",
                 "--python-expr", expr],
                capture_output=True, text=True, timeout=40, check=False,
            )
            lines = [ln.strip() for ln in (proc.stdout or "").splitlines() if ln.strip()]
            blender_python = lines[-2:] if len(lines) >= 2 else None
        except (OSError, subprocess.TimeoutExpired):
            blender_python = None

    return {
        "python": python_info(),
        "tools": tools,
        "blender_python": blender_python,
        "disk": disk_free(Path.home()),
    }


def render(report: dict) -> str:
    lines = []
    lines.append("Motion Studio — environment report")
    lines.append("=" * 44)
    py = report["python"]
    lines.append(f"host            : {py['platform']} ({py['machine']})")
    lines.append(f"python (this)   : {py['version']}  {py['executable']}")
    lines.append(f"disk (home)     : {report['disk']}")
    lines.append("")
    lines.append(f"{'tool':<12}{'status':<10}version")
    lines.append("-" * 60)
    for name, info in report["tools"].items():
        status = "found" if info["found"] else "missing"
        version = (info["version"] or "")[:60]
        lines.append(f"{name:<12}{status:<10}{version}")
    lines.append("")
    if report.get("blender_python"):
        v, exe = report["blender_python"]
        lines.append(f"blender python  : {v}  {exe}")
    else:
        lines.append("blender python  : not detected (fine if Blender is not needed)")
    lines.append("")
    lines.append("Recommended minimum: blender, ffmpeg/ffprobe, node/npm for 2D video.")
    lines.append("Install only what the current project needs.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only environment inventory")
    parser.add_argument("--json", action="store_true", help="print JSON instead of a table")
    parser.add_argument(
        "--required",
        default="",
        help="comma-separated tool names that must exist (e.g. blender,ffmpeg,node)",
    )
    args = parser.parse_args()

    report = collect()
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(render(report))

    required = [t.strip() for t in args.required.split(",") if t.strip()]
    missing = [t for t in required if not report["tools"].get(t, {}).get("found")]
    if missing:
        print(f"\nMISSING REQUIRED: {', '.join(missing)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
