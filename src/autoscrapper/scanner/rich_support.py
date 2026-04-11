from __future__ import annotations

try:
    from rich import box as box
    from rich.align import Align as Align
    from rich.console import Console as Console, Group as Group
    from rich.live import Live as Live
    from rich.panel import Panel as Panel
    from rich.progress import (
        BarColumn as BarColumn,
        Progress as Progress,
        ProgressColumn as ProgressColumn,
        SpinnerColumn as SpinnerColumn,
        Task as Task,
        TaskProgressColumn as TaskProgressColumn,
        TextColumn as TextColumn,
        TimeElapsedColumn as TimeElapsedColumn,
        TimeRemainingColumn as TimeRemainingColumn,
    )
    from rich.table import Table as Table
    from rich.text import Text as Text
except ImportError:  # pragma: no cover - optional dependency
    Align = None
    Console = None
    Group = None
    Live = None
    Panel = None
    BarColumn = None
    Progress = None
    ProgressColumn = None
    SpinnerColumn = None
    Task = None
    TaskProgressColumn = None
    TextColumn = None
    TimeElapsedColumn = None
    TimeRemainingColumn = None
    Table = None
    Text = None
    box = None
