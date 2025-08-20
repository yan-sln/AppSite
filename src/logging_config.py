# -*- coding: utf-8 -*-
"""Logging configuration helper used by the application."""

import logging
from logging import Logger

LOG_FILE = "app_debug.log"


def init_logging(level: int = logging.DEBUG) -> Logger:
    """Initialize root logger with file and console handlers."""
    logger = logging.getLogger()
    if logger.handlers:
        # Already configured
        logger.setLevel(level)
        return logger

    logger.setLevel(level)

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")

    fh = logging.FileHandler(LOG_FILE)
    fh.setLevel(level)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger
