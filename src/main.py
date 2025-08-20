# -*- coding: utf-8 -*-

"""Entry point for the AppSite application."""

from __future__ import annotations

from .logging_config import init_logging
from .app import App

init_logging()


def main() -> None:
    """Create and run the App."""
    app = App()
    app.run()


if __name__ == "__main__":
    main()
