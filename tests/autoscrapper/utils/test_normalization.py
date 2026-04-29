import pytest
from autoscrapper.utils.normalization import normalize_quest_name, normalize_text


def test_normalize_text():
    assert normalize_text("  hello world  ") == "hello world"
    assert normalize_text("hello world") == "hello world"
    assert normalize_text("  \t \n hello world \r \n  ") == "hello world"
    assert normalize_text("") == ""
    assert normalize_text("   ") == ""
    assert normalize_text(None) == ""
    assert normalize_text(123) == ""
    assert normalize_text(["hello"]) == ""
    assert normalize_text({"hello": "world"}) == ""
    assert normalize_text(object()) == ""


def test_normalize_quest_name():
    assert normalize_quest_name("HELLO WORLD") == "hello world"
    assert normalize_quest_name("it's a quest") == "its a quest"
    assert normalize_quest_name("it\u2019s another quest") == "its another quest"
    assert normalize_quest_name("quest-with-dashes! and@symbols") == "quest with dashes and symbols"
    assert normalize_quest_name("   multiple    spaces  in    between   ") == "multiple spaces in between"
    assert normalize_quest_name("  The 'Great' \u2019Quest\u2019: Part-2!  ") == "the great quest part 2"
    assert normalize_quest_name(None) == ""
    assert normalize_quest_name(123) == "123"


@pytest.mark.parametrize(
    "input_val, expected",
    [
        ("Quest Name", "quest name"),
        ("  Quest Name  ", "quest name"),
        ("COLLECTOR'S ITEM", "collectors item"),
        ("Hunter\u2019s Mark", "hunters mark"),
        ('The "Great" Quest', "the great quest"),
        ("Quest: Part 1!", "quest part 1"),
        ("Quest    Name", "quest name"),
        ("  The Elder's @#$% Quest-Line!  ", "the elders quest line"),
        ("", ""),
        (None, ""),
        (0, "0"),
        (False, "false"),
        (123, "123"),
        (45.6, "45 6"),
        ("A+B=C", "a b c"),
    ],
)
def test_normalize_quest_name_parametrized(input_val, expected):
    assert normalize_quest_name(input_val) == expected
