from quest.stats import format_endings_stats, format_stat


def test_format_stat_abs():
    assert format_stat(5, 8, "abs") == "5"


def test_format_stat_rel():
    assert format_stat(5, 8, "rel") == "62.5%"


def test_format_stat_both():
    assert format_stat(5, 8, None) == "5 (62.5%)"


def test_format_stat_zero_total():
    assert format_stat(0, 0, None) == "0 (0.0%)"
    assert format_stat(0, 0, "rel") == "0.0%"


def test_format_endings_stats_sorted_and_formatted():
    lines = format_endings_stats({"dragon": 3, "treasure": 5}, [], None)
    assert lines == ["treasure: 5 (62.5%)", "dragon: 3 (37.5%)"]


def test_format_endings_stats_includes_zero_endings():
    lines = format_endings_stats({"a": 2}, ["a", "b"], "abs")
    assert lines == ["a: 2", "b: 0"]


def test_format_endings_stats_ties_sorted_by_name():
    lines = format_endings_stats({"b": 1, "a": 1}, [], "abs")
    assert lines == ["a: 1", "b: 1"]


def test_format_endings_stats_keeps_unknown_ending_from_db():
    lines = format_endings_stats({"old": 1}, ["a"], "abs")
    assert lines == ["old: 1", "a: 0"]
