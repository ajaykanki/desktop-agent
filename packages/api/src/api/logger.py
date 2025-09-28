import sys
from pathlib import Path
from loguru import logger
from shared import config

def ensure_path_exists(path: str):
    path = Path(path)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)


def setup_logger():
    logger.remove()
    if sys.stdout:
        logger.add(
            sys.stdout,
            level=config.log.level,
            format=config.log.format,
            colorize=config.log.colorize,
            diagnose=config.is_dev,
        )

        if config.log.file:
            ensure_path_exists(config.log.file)
            logger.add(
                config.log.file,
                level=config.log.level,
                format=config.log.format,
                colorize=config.log.colorize,
                rotation=config.log.rotation,
                retention=config.log.retention,
            )

        if config.log.error_file:
            ensure_path_exists(config.log.error_file)
            logger.add(
                config.log.error_file,
                level=config.log.level,
                colorize=config.log.colorize,
                format=config.log.format,
                rotation=config.log.rotation,
                retention=config.log.retention,
            )

    logger.configure(extra={"service": "API"})
    return logger


log = setup_logger()
