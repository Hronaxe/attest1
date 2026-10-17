import logging

import click
from sqlalchemy.exc import SQLAlchemyError

from quest.db import (
    clear_progress,
    count_endings,
    get_session,
    load_progress,
    record_ending,
    save_progress,
)
from quest.logging_config import setup_logging
from quest.stats import format_endings_stats
from quest.story import START_NODE, STORY, is_ending, list_endings, next_node

logger = logging.getLogger(__name__)


def run_game(session, story, new=False):
    if new:
        clear_progress(session)
        logger.info("Начата новая игра (--new)")

    current = load_progress(session)
    if current is None:
        current = START_NODE
        logger.info("Новая игра")
    elif current not in story:
        logger.warning("Сохранённая сцена %r не найдена, игра начата заново", current)
        click.echo("Сохранение повреждено или устарело, начинаем заново.")
        current = START_NODE
    else:
        logger.info("Продолжение игры со сцены %s", current)
        click.echo("Продолжаем сохранённую игру.")

    while True:
        click.echo(f"\n{story[current]['text']}")
        if is_ending(story, current):
            record_ending(session, current)
            logger.info("Достигнута концовка: %s", current)
            click.echo("\nКонец игры.")
            return current

        choice = click.prompt(
            "Ваш выбор",
            type=click.Choice(list(story[current]["choices"])),
        )
        current = next_node(story, current, choice)
        save_progress(session, current)
        logger.info("Выбор %r, переход в сцену %s", choice, current)


def database_error(exc):
    logger.error("Ошибка базы данных: %s", exc, exc_info=exc)
    reason = getattr(exc, "orig", None) or exc.__class__.__name__
    return click.ClickException(f"Ошибка базы данных: {reason}. Подробности в app.log")


@click.group()
def cli():
    try:
        setup_logging()
    except OSError as exc:
        raise click.ClickException(f"Не удалось открыть файл логов: {exc}") from exc


@cli.command()
@click.option("--new", is_flag=True, help="Начать игру заново, забыв сохранение.")
def play(new):
    try:
        with get_session() as session:
            run_game(session, STORY, new=new)
    except SQLAlchemyError as exc:
        raise database_error(exc) from exc


@cli.command()
@click.option(
    "--view",
    type=click.Choice(["abs", "rel"]),
    default=None,
    help="abs — числа, rel — проценты; без опции — оба вида.",
)
def stats(view):
    try:
        with get_session() as session:
            counts = count_endings(session)
    except SQLAlchemyError as exc:
        raise database_error(exc) from exc

    logger.info("Показана статистика (view=%s, концовок в базе: %d)", view, len(counts))
    if not counts:
        click.echo("Завершённых игр пока нет.")
        return
    for line in format_endings_stats(counts, list_endings(STORY), view):
        click.echo(line)
