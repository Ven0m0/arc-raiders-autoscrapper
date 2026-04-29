import pytest
from autoscrapper.utils.normalization import normalize_quest_name


@pytest.mark.parametrize(
    "input_val, expected",
    [
        ("Quest Name", "quest name"),
        ("  Quest Name  ", "quest name"),
        ("COLLECTOR'S ITEM", "collectors item"),
        ("Hunter\u2019s Mark", "hunters mark"),
        ("Quest: Part 1!", "quest part 1"),
        ("Quest    Name", "quest name"),
        ("  The Elder's @#$% Quest-Line!  ", "the elders quest line"),
        ("", ""),
        (None, ""),
        (123, "123"),
        (45.6, "45 6"),
        ("A+B=C", "a b c"),
    ],
)
def test_normalize_quest_name(input_val, expected):
    assert normalize_quest_name(input_val) == expected
