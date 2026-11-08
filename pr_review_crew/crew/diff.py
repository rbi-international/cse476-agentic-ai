"""Read a unified diff: which files changed, and which new lines were added where."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")


@dataclass
class FileChange:
    path: str
    added: dict[int, str] = field(default_factory=dict)  # new line number -> text
    removed: list[str] = field(default_factory=list)

    @property
    def is_python(self) -> bool:
        return self.path.endswith(".py")

    @property
    def is_test(self) -> bool:
        name = self.path.rsplit("/", 1)[-1]
        return name.startswith("test_") or "/tests/" in "/" + self.path


def parse(diff_text: str) -> list[FileChange]:
    files: list[FileChange] = []
    cur: FileChange | None = None
    line_no = 0
    for raw in diff_text.splitlines():
        if raw.startswith("+++ "):
            path = raw[4:].strip()
            if path == "/dev/null":
                cur = None
                continue
            cur = FileChange(path[2:] if path.startswith("b/") else path)
            files.append(cur)
            continue
        if raw.startswith("--- ") or cur is None:
            continue
        m = HUNK.match(raw)
        if m:
            line_no = int(m.group(1))
            continue
        if raw.startswith("+"):
            cur.added[line_no] = raw[1:]
            line_no += 1
        elif raw.startswith("-"):
            cur.removed.append(raw[1:])
        elif raw.startswith(" ") or raw == "":
            line_no += 1
    return files


def is_added(files: list[FileChange], path: str, line: int) -> bool:
    """GitHub only accepts inline comments on lines that are part of the change."""
    return any(f.path == path and line in f.added for f in files)
