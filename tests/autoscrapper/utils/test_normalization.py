
from autoscrapper.utils.normalization import normalize_quest_name, normalize_text


def test_normalize_text():
    # Happy path: strings with surrounding whitespaces
    assert normalize_text("  hello world  ") == "hello world"
    assert normalize_text("hello world") == "hello world"
    assert normalize_text("  \t \n hello world \r \n  ") == "hello world"

    # Edge case: empty strings
    assert normalize_text("") == ""
    assert normalize_text("   ") == ""

    # Error condition/Non-string inputs
    assert normalize_text(None) == ""
    assert normalize_text(123) == ""
    assert normalize_text(["hello"]) == ""
    assert normalize_text({"hello": "world"}) == ""
    assert normalize_text(object()) == ""


def test_normalize_quest_name():
    # Normal case: converts to lowercase
    assert normalize_quest_name("HELLO WORLD") == "hello world"

    # Removes apostrophes and right single quotation marks
    assert normalize_quest_name("it's a quest") == "its a quest"
    assert normalize_quest_name("it\u2019s another quest") == "its another quest"

    # Replaces non-alphanumeric characters with spaces
    assert normalize_quest_name("quest-with-dashes! and@symbols") == "quest with dashes and symbols"

    # Collapses multiple spaces into one and strips
    assert normalize_quest_name("   multiple    spaces  in    between   ") == "multiple spaces in between"

    # Combined edge case
    assert normalize_quest_name("  The 'Great' \u2019Quest\u2019: Part-2!  ") == "the great quest part 2"

    # Non-string inputs
    assert normalize_quest_name(None) == ""
    assert normalize_quest_name(123) == "123"
