import pytest

from quest.story import START_NODE, STORY, is_ending, list_endings, next_node

SMALL = {
    "a": {"text": "A", "choices": {"go": "b"}},
    "b": {"text": "B", "choices": {}},
}


def test_next_node_returns_target():
    assert next_node(SMALL, "a", "go") == "b"


def test_next_node_invalid_choice():
    with pytest.raises(ValueError, match="недопустимый выбор"):
        next_node(SMALL, "a", "nope")


def test_next_node_unknown_scene():
    with pytest.raises(ValueError, match="неизвестная сцена"):
        next_node(SMALL, "zzz", "go")


def test_next_node_from_ending_has_no_choices():
    with pytest.raises(ValueError):
        next_node(SMALL, "b", "go")


def test_is_ending():
    assert is_ending(SMALL, "b") is True
    assert is_ending(SMALL, "a") is False


def test_is_ending_unknown_scene():
    with pytest.raises(ValueError):
        is_ending(SMALL, "zzz")


def test_list_endings():
    assert list_endings(SMALL) == ["b"]


def test_story_start_exists():
    assert START_NODE in STORY


def test_story_all_choices_lead_to_existing_scenes():
    for node_id, node in STORY.items():
        for choice, target in node["choices"].items():
            assert target in STORY, f"{node_id}/{choice} -> {target}"


def test_story_has_at_least_two_endings():
    assert len(list_endings(STORY)) >= 2


def test_story_every_scene_reachable_from_start():
    seen, stack = set(), [START_NODE]
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        stack.extend(STORY[node]["choices"].values())
    assert seen == set(STORY)


def test_story_every_scene_has_text():
    assert all(node["text"].strip() for node in STORY.values())
