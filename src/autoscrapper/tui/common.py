from __future__ import annotations

from functools import cached_property
from typing import ClassVar

from textual import events
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen, Screen
from textual.widget import Widget
from textual.widgets import Button, Static


class AppScreen(Screen):
    BINDINGS: ClassVar[list[Binding | tuple[str, str] | tuple[str, str, str]]] = [
        Binding("escape,ctrl+b", "back", "Back", priority=True)
    ]

    def action_back(self) -> None:
        self.app.pop_screen()


class MessageScreen(ModalScreen[None]):
    DEFAULT_CSS = """
    MessageScreen {
        align: center middle;
    }

    #message-box {
        width: 70%;
        max-width: 80;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #message-text {
        margin-bottom: 1;
    }
    """

    def __init__(self, message: str, *, title: str | None = None) -> None:
        super().__init__()
        self.message = message
        self.title = title or "Notice"

    def compose(self) -> ComposeResult:
        with Vertical(id="message-box"):
            yield Static(self.title or "", classes="modal-title")
            yield Static(self.message, id="message-text")
            yield Button("OK", id="ok", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok":
            self.dismiss()

    def on_key(self, event: events.Key) -> None:
        if event.key in {"escape", "ctrl+b"}:
            self.dismiss()
            event.stop()


def update_inline_filter(event: events.Key, text: str) -> tuple[str, bool]:
    if event.key == "backspace":
        return (text[:-1] if text else text, True)

    character = event.character
    if (
        character
        and len(character) == 1
        and character.isprintable()
        and not event.key.startswith(("ctrl+", "alt+", "meta+"))
    ):
        return (text + character, True)

    return (text, False)


class FormScreen(AppScreen):
    BINDINGS: ClassVar[list[Binding | tuple[str, str] | tuple[str, str, str]]] = [
        *AppScreen.BINDINGS,
        Binding("tab", "focus_next_field", "Next field", show=False, priority=True),
        Binding(
            "shift+tab",
            "focus_previous_field",
            "Previous field",
            show=False,
            priority=True,
        ),
        Binding(
            "up",
            "focus_previous_field",
            "Previous field",
            show=False,
            priority=True,
        ),
        Binding("down", "focus_next_field", "Next field", show=False, priority=True),
    ]

    _FOCUS_ORDER: ClassVar[tuple[str, ...]] = ()

    @property
    def _focus_widgets(self) -> tuple[Widget, ...]:
        return tuple(self.query_one(f"#{widget_id}") for widget_id in self._FOCUS_ORDER)

    def _focus_candidates(self) -> list[Widget]:
        return [w for w in self._focus_widgets if w.is_mounted and w.can_focus and not w.disabled]

    def _cycle_focus(self, delta: int) -> None:
        candidates = self._focus_candidates()
        if not candidates:
            return

        current = self.focused
        if current in candidates:
            index = (candidates.index(current) + delta) % len(candidates)
        else:
            index = 0 if delta > 0 else len(candidates) - 1

        target = candidates[index]
        target.focus()
        target.scroll_visible(immediate=True)

    def action_focus_next_field(self) -> None:
        self._cycle_focus(1)

    def action_focus_previous_field(self) -> None:
        self._cycle_focus(-1)
