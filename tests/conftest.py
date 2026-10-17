import logging

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from quest.db import Base


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


@pytest.fixture
def env(tmp_path, monkeypatch):
    db = tmp_path / "test.db"
    log = tmp_path / "app.log"
    monkeypatch.setenv("QUEST_DB_URL", f"sqlite:///{db}")
    monkeypatch.setenv("QUEST_LOG_FILE", str(log))
    yield {"db": db, "log": log}
    logger = logging.getLogger("quest")
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()
