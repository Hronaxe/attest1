import logging
import os

DEFAULT_LOG_FILE = "app.log"
FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"


def setup_logging(log_file=None):
    path = os.path.abspath(
        log_file or os.environ.get("QUEST_LOG_FILE", DEFAULT_LOG_FILE)
    )
    logger = logging.getLogger("quest")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    for handler in list(logger.handlers):
        if isinstance(handler, logging.FileHandler):
            if handler.baseFilename == path:
                return logger
            logger.removeHandler(handler)
            handler.close()

    handler = logging.FileHandler(path, encoding="utf-8")
    handler.setFormatter(logging.Formatter(FORMAT))
    logger.addHandler(handler)
    return logger
