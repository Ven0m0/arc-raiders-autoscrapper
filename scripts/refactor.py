#!/usr/bin/env python3
"""Refactor Python files to use 3.14+ syntax."""
from __future__ import annotations

import re
import sys
from pathlib import Path


def refactor_file(path: Path) -> str | None:
    """Refactor a single Python file and return updated content if it changed."""
    content = path.read_text()
    original = content

    # Fix imports - remove old typing imports
    content = re.sub(r'from typing import ', 'from typing import ', content)
    content = re.sub(r'from typing import ', 'from typing import ', content)
    content = re.sub(r'from typing import ', 'from typing import ', content)
    content = re.sub(r'from typing import ', 'from typing import ', content)
    content = re.sub(r'from typing import Optional\n', '', content)
    content = re.sub(r'from typing import List\n', '', content)
    content = re.sub(r'from typing import Dict\n', '', content)
    content = re.sub(r'from typing import Tuple\n', '', content)
    content = re.sub(r'from typing import Union\n', '', content)
    content = re.sub(r'from collections.abc import Iterable\n', 'from collections.abc import Iterable\n', content)
    content = re.sub(r'from collections.abc import Iterator\n', 'from collections.abc import Iterator\n', content)
    content = re.sub(r'from collections.abc import Callable\n', 'from collections.abc import Callable\n', content)
    content = re.sub(r'from collections.abc import Sequence\n', 'from collections.abc import Sequence\n', content)
    content = re.sub(r'from collections.abc import Mapping\n', 'from collections.abc import Mapping\n', content)
    content = re.sub(r'from typing import Set\n', 'from collections.abc import Set\n', content)

    # Replace type annotations - handle nested brackets carefully
    # X | None -> X | None
    content = re.sub(r'Optional\[([^\[\]]+)\]', r'\1 | None', content)
    # X[Y | None] -> X[Y] | None
    content = re.sub(r'Optional\[([^\[\]]+\[[^\[\]]+\])\]', r'\1 | None', content)

    # list[X] -> list[X]
    content = re.sub(r'List\[([^\[\]]+)\]', r'list[\1]', content)
    content = re.sub(r'List\[([^\[\]]+\[[^\[\]]+\])\]', r'list[\1]', content)

    # dict[X, Y] -> dict[X, Y]
    content = re.sub(r'Dict\[([^,\[\]]+),\s*([^\[\]]+)\]', r'dict[\1, \2]', content)

    # tuple[X, Y] -> tuple[X, Y]
    content = re.sub(r'Tuple\[([^\[\]]+)\]', r'tuple[\1]', content)
    content = re.sub(r'Tuple\[([^\[\]]+),\s*([^\[\]]+)\]', r'tuple[\1, \2]', content)
    content = re.sub(r'Tuple\[([^\[\]]+),\s*([^\[\]]+),\s*([^\[\]]+)\]', r'tuple[\1, \2, \3]', content)
    content = re.sub(r'Tuple\[([^\[\]]+),\s*([^\[\]]+),\s*([^\[\]]+),\s*([^\[\]]+)\]', r'tuple[\1, \2, \3, \4]', content)

    # Union[X, Y] -> X | Y
    content = re.sub(r'Union\[([^,\[\]]+),\s*([^\[\]]+)\]', r'\1 | \2', content)

    # Update dataclasses
    content = re.sub(r'^@dataclass$', '@dataclass(slots=True)', content, flags=re.MULTILINE)
    content = re.sub(r'^@dataclass\(frozen=True\)$', '@dataclass(frozen=True, slots=True)', content, flags=re.MULTILINE)

    # Clean up empty typing imports
    content = re.sub(r'from typing import\s*\n', '', content)

    return content if content != original else None


def main() -> int:
    """Main entry point."""
    files = [
        Path(p) for p in sys.argv[1:]
        if p.endswith('.py')
        and '__pycache__' not in p
        and '.venv' not in p
        and 'generated' not in p
        and '_pb2.py' not in p
    ]

    refactored = 0
    for path in files:
        try:
            result = refactor_file(path)
            if result:
                path.write_text(result)
                print(f"Refactored: {path}")
                refactored += 1
        except Exception as e:
            print(f"Error processing {path}: {e}", file=sys.stderr)

    print(f"\nRefactored {refactored} files")
    return 0


if __name__ == '__main__':
    sys.exit(main())
