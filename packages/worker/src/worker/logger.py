import sys
from loguru import logger
from worker.config import config


def setup_logger():
    logger.remove()
    logger.add(
        sys.stdout,
        level=config.logging.level,
        format=config.logging.format,
        colorize=True,
    )
    if config.logging.file:
        logger.add(
            config.logging.file,
            level=config.logging.level,
            rotation=config.logging.rotation,
            retention=config.logging.retention,
            compression=config.logging.compression,
            colorize=config.logging.colorize,
        )

    if config.logging.error_file:
        logger.add(
            config.logging.error_file,
            level="ERROR",
            rotation=config.logging.rotation,
            retention=config.logging.retention,
            compression=config.logging.compression,
            colorize=config.logging.colorize,
        )

    return logger


log = setup_logger()
