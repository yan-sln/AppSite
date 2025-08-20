# -*- coding: utf-8 -*-
"""Constants for the AppSite project."""

from pathlib import Path

# Repository root (parent of src/)
REPO_ROOT: Path = Path(__file__).resolve().parents[1]

# Templates directory at repository root
TEMPLATES_DIR: Path = REPO_ROOT / "templates"
HEADER_TEMPLATE_FILE: str = "post_header.jinja"
FOOTER_TEMPLATE_FILE: str = "post_footer.jinja"

# Resources folders
NEEDS_DIR: Path = REPO_ROOT / "needs"
RESOURCES_DIR: Path = REPO_ROOT / "resources"

# Default runtime dirs (created in working directory)
TEMP_DIR_NAME: str = "temp"
EXP_DIR_NAME: str = "exp"
