import unittest

from autoscrapper.items.rules_diff import collect_rule_changes
from autoscrapper.progress.data_loader import load_game_data
from autoscrapper.progress.rules_generator import generate_rules_from_active


class ProgressCompatibilityTests(unittest.TestCase):
    def test_bundled_data_generates_rules_for_new_and_completed_progress(self):
        data = load_game_data()
        self.assertTrue(data.items)
        self.assertTrue(data.quests)
        completed = generate_rules_from_active([], {}, all_quests_completed=True)
        starting = generate_rules_from_active([], {}, completed_quests_override=[])
        self.assertGreater(len(completed["items"]), 0)
        self.assertEqual(len(completed["items"]), len(starting["items"]))
        for payload in (completed, starting):
            self.assertTrue(
                all(
                    item["action"] in {"keep", "sell", "recycle"}
                    for item in payload["items"]
                )
            )
        self.assertTrue(collect_rule_changes(completed, starting))
