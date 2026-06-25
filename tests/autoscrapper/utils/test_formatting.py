from autoscrapper.utils.formatting import format_duration


def test_format_duration():
    assert format_duration(None) == "--:--"
    assert format_duration(float("nan")) == "--:--"
    assert format_duration(float("inf")) == "--:--"
    assert format_duration(-10) == "00:00"
    assert format_duration(0) == "00:00"
    assert format_duration(45) == "00:45"
    assert format_duration(65) == "01:05"
    assert format_duration(3665) == "1:01:05"
    assert format_duration(125.5) == "02:05"
