"""API settings screen for ArcTracker integration."""

from __future__ import annotations

from dataclasses import replace

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, HorizontalGroup, Vertical
from textual.widget import Widget
from textual.widgets import Button, Checkbox, Footer, Input, Static

from .common import AppScreen, MessageScreen
from ..config import load_api_settings, reset_api_settings, save_api_settings


class ApiSettingsScreen(AppScreen):
    """Screen for configuring ArcTracker API integration."""

    BINDINGS = [
        *AppScreen.BINDINGS,
        Binding("tab", "focus_next_field", "Next field", show=False, priority=True),
        Binding(
            "shift+tab",
            "action_focus_previous_field",
            "Previous field",
            show=False,
            priority=True,
        ),
        Binding(
            "up",
            "action_focus_previous_field",
            "Previous field",
            show=False,
            priority=True,
        ),
        Binding("down", "focus_next_field", "Next field", show=False, priority=True),
    ]

    TITLE = "API Settings (ArcTracker)"
    _FOCUS_ORDER = (
        "enabled",
        "app-key",
        "user-key",
        "prefer-api",
        "save",
        "back",
    )

    DEFAULT_CSS = """
    ApiSettingsScreen {
        padding: 0 1;
    }

    ApiSettingsScreen .menu-title {
        margin: 0;
    }

    #api-settings-shell {
        width: 100%;
        height: 1fr;
        layout: vertical;
        border: round #334155;
        background: #0b1220;
        padding: 0 1;
        overflow: hidden hidden;
    }

    #api-settings-form {
        width: 100%;
        height: 1fr;
        overflow-y: auto;
        overflow-x: hidden;
    }

    .setting-row {
        width: 1fr;
        height: auto;
        align: left middle;
    }

    .setting-label-col {
        width: 20;
        color: $text-muted;
        margin-right: 1;
    }

    .setting-control-row {
        height: auto;
        align: left middle;
        margin-top: 0;
    }

    .setting-value {
        width: 40;
        min-width: 40;
        min-height: 3;
        content-align: left middle;
        text-style: bold;
        border: round #334155;
        background: #111827;
        padding: 0 1;
        margin-right: 1;
    }

    .field-input {
        width: 40;
        min-width: 40;
        max-width: 40;
        min-height: 3;
        padding: 0 1;
    }

    .api-info {
        color: $text-muted;
        margin-top: 1;
        margin-bottom: 1;
    }

    #screen-actions {
        margin-top: 0;
        height: auto;
        align: left middle;
    }

    #screen-actions Button {
        min-width: 12;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self.settings = load_api_settings()

    def compose(self) -> ComposeResult:
        yield Static(self.TITLE, classes="menu-title")
        with Vertical(id="api-settings-shell"):
            with Vertical(id="api-settings-form"):
                yield from self._compose_form()
            with Horizontal(id="screen-actions"):
                yield Button("Save", id="save", variant="primary")
                yield Button("Back", id="back")
        yield Footer()

    def on_mount(self) -> None:
        self._load_into_fields()
        self.action_focus_next_field()

    def _focus_candidates(self) -> list[Widget]:
        candidates: list[Widget] = []
        for widget_id in self._FOCUS_ORDER:
            widget = self.query_one(f"#{widget_id}")
            if getattr(widget, "disabled", False):
                continue
            candidates.append(widget)
        return candidates

    def _move_focus(self, delta: int) -> None:
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
        self._move_focus(1)

    def action_focus_previous_field(self) -> None:
        self._move_focus(-1)

    def _compose_form(self) -> ComposeResult:
        yield Static(
            "Configure ArcTracker.io API access. Public endpoints work without keys.",
            classes="api-info",
        )

        with HorizontalGroup(classes="setting-row"):
            yield Static("Enable API", classes="setting-label-col")
            yield Checkbox(id="enabled")

        with HorizontalGroup(classes="setting-row"):
            yield Static("App Key", classes="setting-label-col")
            yield Input(
                id="app-key",
                classes="field-input",
                placeholder="Your registered app key",
                password=True,
            )

        with HorizontalGroup(classes="setting-row"):
            yield Static("User Key", classes="setting-label-col")
            yield Input(
                id="user-key",
                classes="field-input",
                placeholder="Your personal user key",
                password=True,
            )

        with HorizontalGroup(classes="setting-row"):
            yield Static("Prefer API", classes="setting-label-col")
            yield Checkbox(id="prefer-api")

        yield Static(
            "User endpoints (/api/v2/user/*) require both keys. Auto-fallback to OCR on API failure.",
            classes="api-info",
        )

    def _load_into_fields(self) -> None:
        self.settings = load_api_settings()
        self.query_one("#enabled", Checkbox).value = self.settings.enabled
        self.query_one("#app-key", Input).value = self.settings.app_key
        self.query_one("#user-key", Input).value = self.settings.user_key
        self.query_one("#prefer-api", Checkbox).value = self.settings.prefer_api

    def _save(self) -> None:
        updated = replace(
            self.settings,
            enabled=self.query_one("#enabled", Checkbox).value,
            app_key=self.query_one("#app-key", Input).value.strip(),
            user_key=self.query_one("#user-key", Input).value.strip(),
            prefer_api=self.query_one("#prefer-api", Checkbox).value,
        )
        self.settings = updated
        save_api_settings(updated)
        self.app.push_screen(MessageScreen("API settings saved."))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            self._save()
        elif event.button.id == "back":
            self.app.pop_screen()


class ResetApiSettingsScreen(AppScreen):
    """Screen for resetting API settings to defaults."""

    DEFAULT_CSS = """
    ResetApiSettingsScreen {
        padding: 0 1;
    }

    ResetApiSettingsScreen .menu-title {
        margin: 0 0 1 0;
    }

    #api-reset-shell {
        width: 100%;
        border: round #334155;
        background: #0b1220;
        padding: 0 1;
    }

    #api-reset-actions {
        margin-top: 0;
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("Reset API Settings", classes="menu-title")
        with Vertical(id="api-reset-shell"):
            yield Static(
                "This clears all API settings including keys. Are you sure?",
                classes="hint",
            )
            with Horizontal(id="api-reset-actions"):
                yield Button("Cancel", id="cancel")
                yield Button("Reset", id="reset", variant="warning")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.app.pop_screen()
        elif event.button.id == "reset":
            reset_api_settings()
            self.app.pop_screen()
            self.app.push_screen(MessageScreen("API settings reset to defaults."))
