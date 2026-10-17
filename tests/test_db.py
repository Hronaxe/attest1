import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from quest.db import (
    Ending,
    Progress,
    clear_progress,
    count_endings,
    get_session,
    load_progress,
    record_ending,
    save_progress,
)


def test_load_progress_empty(session):
    assert load_progress(session) is None


def test_save_and_load_progress(session):
    save_progress(session, "cave")
    assert load_progress(session) == "cave"


def test_save_progress_overwrites_single_row(session):
    save_progress(session, "cave")
    save_progress(session, "hall")
    assert load_progress(session) == "hall"
    assert session.scalar(select(func.count()).select_from(Progress)) == 1


def test_clear_progress(session):
    save_progress(session, "cave")
    clear_progress(session)
    assert load_progress(session) is None


def test_clear_progress_when_empty_is_noop(session):
    clear_progress(session)
    assert load_progress(session) is None


def test_record_ending_clears_progress(session):
    save_progress(session, "treasure")
    record_ending(session, "treasure")
    assert load_progress(session) is None
    assert count_endings(session) == {"treasure": 1}


def test_count_endings_empty(session):
    assert count_endings(session) == {}


def test_count_endings_accumulates_across_games(session):
    for node in ["treasure", "dragon", "treasure"]:
        record_ending(session, node)
    assert count_endings(session) == {"treasure": 2, "dragon": 1}


def test_record_ending_stores_timestamp(session):
    record_ending(session, "dragon")
    assert session.scalar(select(Ending.created_at)) is not None


def test_failed_transaction_rolls_back_and_raises(session):
    save_progress(session, "cave")
    with pytest.raises(SQLAlchemyError):
        record_ending(session, None)  # node_id NOT NULL
    assert load_progress(session) == "cave"
    assert count_endings(session) == {}


def test_get_session_creates_tables_and_persists(tmp_path):
    url = f"sqlite:///{tmp_path / 'x.db'}"
    with get_session(url) as s:
        save_progress(s, "river")
    with get_session(url) as s:
        assert load_progress(s) == "river"


def test_get_session_uses_env_url(tmp_path, monkeypatch):
    monkeypatch.setenv("QUEST_DB_URL", f"sqlite:///{tmp_path / 'env.db'}")
    with get_session() as s:
        save_progress(s, "hall")
    assert (tmp_path / "env.db").exists()
