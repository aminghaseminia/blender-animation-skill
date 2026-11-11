#!/usr/bin/env python3
"""Validate the skill pack: frontmatter, naming, links, scripts.

Usage:
    python3 scripts/validate_skills.py

Exit code 0 when everything passes, 1 when there are errors.
Warnings do not fail the build.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
REQUIRED_KEYS = ("name", "description")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
MAX_LINES = 600

errors: list[str] = []
warnings: list[str] = []


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end]
    data: dict[str, str] = {}
    key = None
    for raw in block.splitlines():
        if not raw.strip():
            continue
        if raw.startswith((" ", "\t")) and key:
            data[key] += " " + raw.strip()
            continue
        if ":" in raw and not raw.startswith(" "):
            k, _, v = raw.partition(":")
            key = k.strip()
            data[key] = v.strip()
    return data


def check_skill(skill_dir: Path) -> None:
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        errors.append(f"{skill_dir.name}: missing SKILL.md")
        return

    text = skill_file.read_text(encoding="utf-8")
    meta = parse_frontmatter(text)

    for key in REQUIRED_KEYS:
        if not meta.get(key):
            errors.append(f"{skill_dir.name}: missing frontmatter key '{key}'")

    if meta.get("name") and meta["name"] != skill_dir.name:
        errors.append(
            f"{skill_dir.name}: frontmatter name '{meta['name']}' does not match folder"
        )

    desc = meta.get("description", "")
    if desc and len(desc) < 60:
        warnings.append(f"{skill_dir.name}: description is short ({len(desc)} chars)")
    if len(desc) > 1200:
        warnings.append(f"{skill_dir.name}: description is very long ({len(desc)} chars)")

    lines = text.count("\n") + 1
    if lines > MAX_LINES:
        warnings.append(f"{skill_dir.name}: SKILL.md is {lines} lines (> {MAX_LINES})")

    if text.count("```") % 2 != 0:
        errors.append(f"{skill_dir.name}: unbalanced fenced code blocks")

    # relative markdown links must resolve within the skill folder
    for raw_link in LINK_RE.findall(text):
        link = raw_link.split("#", 1)[0].strip()
        if not link or link.startswith(("http://", "https://", "mailto:", "tel:")):
            continue
        target = (skill_dir / link).resolve()
        if not target.exists():
            errors.append(f"{skill_dir.name}: broken relative link '{link}'")

    # every reference file should be mentioned somewhere in the skill
    refs = skill_dir / "references"
    if refs.is_dir():
        for ref in sorted(refs.glob("*.md")):
            if ref.name not in text:
                warnings.append(
                    f"{skill_dir.name}: references/{ref.name} is not mentioned in SKILL.md"
                )


def check_scripts() -> None:
    for sh in SKILLS.rglob("*.sh"):
        if not sh.read_text(encoding="utf-8").startswith("#!"):
            warnings.append(f"{sh.relative_to(ROOT)}: missing shebang")
    for py in SKILLS.rglob("*.py"):
        if not py.read_text(encoding="utf-8").startswith("#!"):
            warnings.append(f"{py.relative_to(ROOT)}: missing shebang")


def main() -> int:
    if not SKILLS.is_dir():
        print("skills/ not found", file=sys.stderr)
        return 1

    skill_dirs = sorted(d for d in SKILLS.iterdir() if d.is_dir())
    if not skill_dirs:
        errors.append("no skills found")

    for d in skill_dirs:
        check_skill(d)
    check_scripts()

    for w in warnings:
        print(f"warn  {w}")
    for e in errors:
        print(f"ERROR {e}")

    print(f"\n{len(skill_dirs)} skills checked · {len(errors)} error(s) · {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
