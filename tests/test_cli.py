import logging

import pytest
from click.testing import CliRunner
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from quest.cli import cli, run_game
from quest.db import Base, count_endings, get_session, load_progress, save_progress
from quest.logging_config import setup_logging
from quest.story import STORY

TREASURE = "north\nenter\nsneak\n"


@pytest.fixture
def runner():
    return CliRunner()


def test_play_reaches_ending_and_records_it(runner, env):
    result = runner.invoke(cli, ["play"], input=TREASURE)
    assert result.exit_code == 0
    assert "Конец игры" in result.output
    with get_session() as s:
        assert count_endings(s) == {"treasure": 1}
        assert load_progress(s) is None


def test_play_resumes_saved_scene(runner, env):
    with get_session() as s:
        save_progress(s, "hall")
    result = runner.invoke(cli, ["play"], input="attack\n")
    assert result.exit_code == 0
    assert "Продолжаем" in result.output
    with get_session() as s:
        assert count_endings(s) == {"dragon": 1}


def test_play_new_discards_saved_progress(runner, env):
    with get_session() as s:
        save_progress(s, "hall")
    result = runner.invoke(cli, ["play", "--new"], input=TREASURE)
    assert result.exit_code == 0
    assert "Продолжаем" not in result.output


def test_play_saves_progress_after_each_step_on_abort(runner, env):
    result = runner.invoke(cli, ["play"], input="north\n")
    assert result.exit_code != 0
    with get_session() as s:
        assert load_progress(s) == "cave"


def test_play_invalid_choice_is_reprompted(runner, env):
    result = runner.invoke(cli, ["play"], input="west\n" + TREASURE)
    assert result.exit_code == 0
    assert "Error" in result.output or "not one of" in result.output


def test_play_unknown_saved_scene_restarts(runner, env):
    with get_session() as s:
        save_progress(s, "removed_scene")
    result = runner.invoke(cli, ["play"], input=TREASURE)
    assert result.exit_code == 0
    assert "начинаем заново" in result.output


def test_stats_empty(runner, env):
    result = runner.invoke(cli, ["stats"])
    assert result.exit_code == 0
    assert "пока нет" in result.output


def test_stats_both_views_by_default(runner, env):
    runner.invoke(cli, ["play"], input=TREASURE)
    runner.invoke(cli, ["play"], input="north\nenter\nattack\n")
    result = runner.invoke(cli, ["stats"])
    assert result.exit_code == 0
    assert "dragon: 1 (50.0%)" in result.output
    assert "treasure: 1 (50.0%)" in result.output
    assert "village: 0 (0.0%)" in result.output


def test_stats_abs_and_rel(runner, env):
    runner.invoke(cli, ["play"], input=TREASURE)
    assert "treasure: 1\n" in runner.invoke(cli, ["stats", "--view", "abs"]).output
    assert "treasure: 100.0%" in runner.invoke(cli, ["stats", "--view", "rel"]).output


def test_stats_invalid_view_exit_code(runner, env):
    result = runner.invoke(cli, ["stats", "--view", "xxx"])
    assert result.exit_code == 2
    assert "Invalid value" in result.output


def test_database_error_gives_clean_message_and_nonzero_exit(runner, env, monkeypatch):
    monkeypatch.setenv("QUEST_DB_URL", "sqlite:////nonexistent_dir/sub/x.db")
    for args in (["play"], ["stats"]):
        result = runner.invoke(cli, args, input=TREASURE)
        assert result.exit_code == 1
        assert "Ошибка базы данных: unable to open database file" in result.output
        assert "Traceback" not in result.output


def test_unwritable_log_file_gives_clean_error(runner, env, monkeypatch):
    monkeypatch.setenv("QUEST_LOG_FILE", "/nonexistent_dir/app.log")
    result = runner.invoke(cli, ["stats"])
    assert result.exit_code == 1
    assert "файл логов" in result.output


def test_events_and_errors_are_logged(runner, env, monkeypatch):
    runner.invoke(cli, ["play"], input=TREASURE)
    monkeypatch.setenv("QUEST_DB_URL", "sqlite:////nonexistent_dir/x.db")
    runner.invoke(cli, ["stats"])
    for handler in logging.getLogger("quest").handlers:
        handler.flush()
    text = env["log"].read_text(encoding="utf-8")
    assert "Достигнута концовка: treasure" in text
    assert "ERROR" in text


def test_run_game_returns_ending_id(monkeypatch):
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    answers = iter(["south", "bridge"])
    monkeypatch.setattr("click.prompt", lambda *a, **k: next(answers))
    with Session(engine) as s:
        assert run_game(s, STORY) == "village"


def test_setup_logging_is_idempotent(tmp_path):
    path = tmp_path / "a.log"
    logger = setup_logging(str(path))
    setup_logging(str(path))
    try:
        file_handlers = [
            h for h in logger.handlers if isinstance(h, logging.FileHandler)
        ]
        assert len(file_handlers) == 1
    finally:
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
            handler.close()


def test_stats_call_is_logged(runner, env):
    runner.invoke(cli, ["stats", "--view", "abs"])
    for handler in logging.getLogger("quest").handlers:
        handler.flush()
    assert "Показана статистика (view=abs" in env["log"].read_text(encoding="utf-8")
