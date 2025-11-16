import os
import sys
from loguru import logger


class LoggerConfig:
    def __init__(self):
        self.env = os.getenv("ENV", "dev").lower()
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.log_format = self._get_log_format()
        self.log_rotation = os.getenv("LOG_ROTATION", "1 month")
        self.log_retention = os.getenv("LOG_RETENTION")
        self.log_compression = os.getenv("LOG_COMPRESSION", "zip")
        self.log_file = os.getenv("LOG_FILE")
        self.log_error_file = os.getenv("LOG_ERROR_FILE")

    def _get_log_format(self) -> str:
        """Get appropriate log format based on environment."""
        custom_format = os.getenv("LOG_FORMAT")
        if custom_format:
            return custom_format

        if self.env in ["prod", "production"]:
            return "<g>{time: DD-MM-YYYY hh:mm:ss A}</g> | <level>[{level}] {message}</level>"
        else:
            return "<g>{time: DD-MM-YYYY hh:mm:ss A}</g> | <level>[{level}]</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"


def _setup_logger_handlers(config: LoggerConfig) -> None:
    logger.remove()
    logger.add(
        sys.stdout,
        level=config.log_level,
        format=config.log_format,
        diagnose=(config.env == "dev"),
        colorize=True,
    )
    if config.log_file:
        try:
            logger.add(
                config.log_file,
                level=config.log_level,
                format=config.log_format,
                rotation=config.log_rotation,
                retention=config.log_retention,
                compression=config.log_compression,
                backtrace=True,
                catch=True,
            )
        except Exception as e:
            logger.error(f"Failed to add file handler for {config.log_file}: {e}")

    # Add error file handler if specified
    if config.log_error_file:
        try:
            logger.add(
                config.log_error_file,
                level="ERROR",  # Error file should only log errors
                format=config.log_format,
                rotation=config.log_rotation,
                retention=config.log_retention,
                compression=config.log_compression,
                backtrace=True,
                catch=True,
            )
        except Exception as e:
            logger.error(
                f"Failed to add error file handler for {config.log_error_file}: {e}"
            )


_logger_config = LoggerConfig()
_setup_logger_handlers(_logger_config)
log = logger
