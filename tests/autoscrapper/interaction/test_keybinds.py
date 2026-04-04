import pytest
from autoscrapper.interaction.keybinds import stop_key_label

@pytest.mark.parametrize(
    "key, expected_label",
    [
        # Canonical display keys
        ("escape", "Esc"),
        ("esc", "Esc"),
        ("enter", "Enter"),
        ("space", "Space"),
        ("spacebar", "Space"),
        ("tab", "Tab"),
        ("backspace", "Backspace"),
        ("delete", "Delete"),
        ("del", "Delete"),
        ("insert", "Insert"),
        ("ins", "Insert"),
        ("home", "Home"),
        ("end", "End"),
        ("pageup", "Page Up"),
        ("pgup", "Page Up"),
        ("page_up", "Page Up"),
        ("pagedown", "Page Down"),
        ("pgdn", "Page Down"),
        ("page_down", "Page Down"),
        ("up", "Up Arrow"),
        ("down", "Down Arrow"),
        ("left", "Left Arrow"),
        ("right", "Right Arrow"),

        # Function keys
        ("f1", "F1"),
        ("f5", "F5"),
        ("f12", "F12"),

        # Single characters
        ("a", "A"),
        ("Z", "Z"),
        ("1", "1"),
        ("-", "-"),
        ("=", "="),
        ("[", "["),

        # Edge cases and invalid inputs (fallback to DEFAULT_STOP_KEY which is 'escape')
        (None, "Esc"),
        (123, "Esc"),
        ("", "Esc"),
        ("   ", "Esc"),
        ("invalid_key", "Esc"),

        # Whitespace handling
        ("  f1  ", "F1"),
        ("  a  ", "A"),
    ]
)
def test_stop_key_label(key, expected_label):
    assert stop_key_label(key) == expected_label
