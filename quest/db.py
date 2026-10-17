import logging
import os
from contextlib import contextmanager
from datetime import datetime, timezone

from sqlalchemy import create_engine, delete, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

logger = logging.getLogger(__name__)

DEFAULT_DB_URL = "sqlite:///stats.db"
PROGRESS_ID = 1


class Base(DeclarativeBase):
    pass


class Progress(Base):
    __tablename__ = "progress"

    id: Mapped[int] = mapped_column(primary_key=True)
    node_id: Mapped[str]


class Ending(Base):
    __tablename__ = "endings"

    id: Mapped[int] = mapped_column(primary_key=True)
    node_id: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )


@contextmanager
def get_session(url=None):
    url = url or os.environ.get("QUEST_DB_URL", DEFAULT_DB_URL)
    engine = create_engine(url)
    try:
        Base.metadata.create_all(engine)
        with Session(engine) as session:
            yield session
    finally:
        engine.dispose()


@contextmanager
def transaction(session):
    try:
        yield
        session.commit()
    except Exception as exc:
        session.rollback()
        logger.warning("Транзакция откачена (%s)", exc.__class__.__name__)
        raise


def save_progress(session, node_id):
    with transaction(session):
        session.merge(Progress(id=PROGRESS_ID, node_id=node_id))


def load_progress(session):
    return session.scalar(select(Progress.node_id).where(Progress.id == PROGRESS_ID))


def clear_progress(session):
    with transaction(session):
        session.execute(delete(Progress))


def record_ending(session, node_id):
    with transaction(session):
        session.add(Ending(node_id=node_id))
        session.execute(delete(Progress))


def count_endings(session):
    rows = session.execute(
        select(Ending.node_id, func.count()).group_by(Ending.node_id)
    ).all()
    return {node_id: count for node_id, count in rows}
