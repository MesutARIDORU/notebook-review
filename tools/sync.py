#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Copies the notebook into a skill.

  python3 tools/sync.py ../insanlik-oldu-mu           # replaces <skill>/notebook with this notebook
  python3 tools/sync.py ../insanlik-oldu-mu --check   # exits with 1 when the skill's copy differs

The skill keeps its own notebook.json and scripts; only the notebook/ folder is replaced.
Uses only the Python 3 standard library.
"""

import argparse
import filecmp
import os
import shutil
import sys

KIT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "notebook")
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store")


def differences(a, b):
    """Relative paths that differ between two folders (missing on either side or changed)."""
    out = []
    cmp = filecmp.dircmp(a, b, ignore=["__pycache__", ".DS_Store"])

    def walk(c, prefix):
        out.extend(os.path.join(prefix, n) for n in c.left_only + c.right_only)
        _, mismatch, errors = filecmp.cmpfiles(c.left, c.right, c.common_files, shallow=False)
        out.extend(os.path.join(prefix, n) for n in mismatch + errors)
        for name, sub in c.subdirs.items():
            walk(sub, os.path.join(prefix, name))
    walk(cmp, "")
    return sorted(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Copies the notebook into a skill")
    ap.add_argument("skill", help="the skill's folder (the one with notebook.json)")
    ap.add_argument("--check", action="store_true", help="only report whether the copy is up to date")
    a = ap.parse_args(argv)

    skill = os.path.abspath(a.skill)
    if not os.path.exists(os.path.join(skill, "notebook.json")):
        sys.exit(f"{skill} has no notebook.json; is it a skill that uses the notebook?")
    target = os.path.join(skill, "notebook")
    with open(os.path.join(KIT, "VERSION"), encoding="utf-8") as f:
        version = f.read().strip()

    changed = differences(KIT, target) if os.path.isdir(target) else ["notebook/"]
    if a.check:
        if changed:
            print(f"out of date with notebook {version}: " + ", ".join(changed))
            return 1
        print(f"up to date with notebook {version}")
        return 0
    if not changed:
        print(f"already up to date with notebook {version}")
        return 0
    if os.path.isdir(target):
        shutil.rmtree(target)
    shutil.copytree(KIT, target, ignore=IGNORE)
    print(f"notebook {version} copied into {target} ({len(changed)} changed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
