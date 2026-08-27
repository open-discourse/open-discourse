"""Checks the raw session XML downloads for gaps in the session numbering per
electoral term, without downloading or deleting anything.

Run after any download stage to confirm nothing was silently missed.
"""

import re
import sys
from pathlib import Path

import od_lib.definitions.path_definitions as path_definitions

# (label, root folder, glob for one term's session files)
SOURCES = [
    ("WP1-18", path_definitions.RAW_XML, "electoral_term_*", "*.xml"),
    (
        "WP19+",
        path_definitions.ELECTORAL_TERM_19_20_STAGE_01,
        "electoral_term_*",
        "*.xml",
    ),
]


def session_numbers(folder: Path, term_len: int):
    nums = []
    for f in folder.glob("*.xml"):
        m = re.match(rf"^\d{{{term_len}}}(\d+)$", f.stem)
        if m:
            nums.append(int(m.group(1)))
    return sorted(nums)


def check_source(label, root):
    if not root.exists():
        return []
    problems = []
    for term_folder in sorted(root.glob("electoral_term_*")):
        if not term_folder.is_dir():
            continue
        term = term_folder.name.replace("electoral_term_", "")
        nums = session_numbers(term_folder, len(term))
        if not nums:
            continue
        expected = set(range(nums[0], nums[-1] + 1))
        missing = sorted(expected - set(nums))
        status = f"{label} WP{term}: {len(nums)} files, range {nums[0]}-{nums[-1]}"
        if missing:
            status += f" -- MISSING: {missing}"
            problems.append((label, term, missing))
        print(status)
    return problems


def main():
    all_problems = []
    for label, root, *_ in SOURCES:
        all_problems += check_source(label, root)
    if all_problems:
        print(f"\n{len(all_problems)} term(s) with gaps - re-run that term's download stage.")
        sys.exit(1)
    print("\nNo gaps found.")


if __name__ == "__main__":
    main()
