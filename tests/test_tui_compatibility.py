import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from autoscrapper import config
from autoscrapper.core.item_actions import ItemActionResult
from autoscrapper.interaction.inventory_grid import Cell
from autoscrapper.items import rules_store
from autoscrapper.scanner.types import ScanStats


class TuiCompatibilityTests(unittest.IsolatedAsyncioTestCase):
    async def test_screens_filter_sort_and_render_results(self):
        # Desktop polling is outside this headless test; retain the real UI.
        desktop = types.ModuleType("autoscrapper.interaction.ui_windows")
        desktop.TARGET_APP = "Arc Raiders"
        desktop.WINDOW_TIMEOUT = 30
        desktop.WindowSnapshot = object
        desktop.build_window_snapshot = lambda window: None
        desktop.get_active_target_window = lambda: None
        desktop.stop_key_pressed = lambda key: False

        with (
            tempfile.TemporaryDirectory() as directory,
            patch.dict(sys.modules, {desktop.__name__: desktop}),
            patch.object(
                config, "config_path", return_value=Path(directory) / "config.json"
            ),
            patch.object(
                rules_store, "CUSTOM_RULES_PATH", Path(directory) / "rules.json"
            ),
        ):
            from textual.widgets import DataTable, Input, OptionList

            from autoscrapper.tui import app as app_module
            from autoscrapper.tui.app import AutoScrapperApp, HomeScreen
            from autoscrapper.tui.progress import ActiveQuestsScreen
            from autoscrapper.tui.progress.review import ReviewQuestsScreen
            from autoscrapper.tui.progress.state import build_wizard_state
            from autoscrapper.tui.rules import RulesScreen
            from autoscrapper.tui.scan import ScanResultsScreen
            from autoscrapper.tui.settings import (
                CaptureStopKeyScreen,
                ScanControlsScreen,
            )

            class HeadlessApp(AutoScrapperApp):
                CSS_PATH = Path(app_module.__file__).with_name("app.tcss")

                def on_mount(self):
                    # Skip background desktop/OCR warmup; OCR is tested separately.
                    self.push_screen(HomeScreen())

            state = build_wizard_state()
            app = HeadlessApp()
            async with app.run_test(size=(120, 45)) as pilot:
                await pilot.pause()
                self.assertGreater(app.screen.query_one(OptionList).option_count, 0)

                for screen in (
                    RulesScreen(),
                    ActiveQuestsScreen(state),
                    ReviewQuestsScreen(state.quest_entries, config.ProgressSettings()),
                ):
                    with self.subTest(screen=type(screen).__name__):
                        await app.push_screen(screen)
                        await pilot.pause()
                        menu = screen.query_one(OptionList)
                        original_count = menu.option_count
                        self.assertGreater(original_count, 0)
                        search = next(
                            widget
                            for widget in screen.query(Input)
                            if "search" in (widget.id or "")
                        )
                        search.value = "no_matching_item_or_quest_987654321"
                        await pilot.pause()
                        self.assertEqual(menu.option_count, 0)
                        search.value = ""
                        await pilot.pause()
                        self.assertEqual(menu.option_count, original_count)
                        previous_sort = screen.sort_mode
                        screen.action_cycle_sort()
                        await pilot.pause()
                        self.assertNotEqual(screen.sort_mode, previous_sort)
                        self.assertEqual(menu.option_count, original_count)
                        app.pop_screen()
                        await pilot.pause()

                controls = ScanControlsScreen()
                await app.push_screen(controls)
                await pilot.pause()
                controls.action_focus_next_field()
                controls.action_focus_previous_field()
                self.assertIsNotNone(controls.focused)
                app.pop_screen()
                await pilot.pause()

                capture = CaptureStopKeyScreen()
                await app.push_screen(capture)
                await pilot.pause()
                await pilot.press("f9")
                self.assertEqual(capture._pending_key.lower(), "f9")
                app.pop_screen()
                await pilot.pause()

                result = ItemActionResult(
                    page=0,
                    cell=Cell(0, 0, 0, 0, 0, 95, 95, (10, 10, 85, 85)),
                    item_name="Test item",
                    decision="KEEP",
                    action_taken="KEEP",
                )
                results = ScanResultsScreen(
                    results=[result],
                    stats=ScanStats(1, "1", 1, 1, 0.5),
                    dry_run=True,
                )
                await app.push_screen(results)
                await pilot.pause()
                self.assertEqual(results.query_one(DataTable).row_count, 1)

            self.assertEqual(list(Path(directory).iterdir()), [])
