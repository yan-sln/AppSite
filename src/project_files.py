# -*- coding: utf-8 -*-

"""ProjectFiles: centralizes file operations and HTML generation using Jinja2."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, Template
from . import constants
import logging

logger = logging.getLogger(__name__)

JINJA_ENV = Environment(
    loader=FileSystemLoader(str(constants.TEMPLATES_DIR)),
    autoescape=True,
)


class ProjectFiles:
    """Manage temporary and export directories and post.html files."""

    def __init__(self, temp_dir: str = constants.TEMP_DIR_NAME, exp_dir: str = constants.EXP_DIR_NAME, auto_create: bool = False):
        self.temp_dir = Path(temp_dir)
        self.exp_dir = Path(exp_dir)
        self.temp_post = self.temp_dir / "post.html"
        self.exp_post = self.exp_dir / "post.html"
        self._footer_content: Optional[str] = None
        if auto_create:
            self.ensure_dirs()

    def ensure_dirs(self) -> None:
        """Create required directories for temp and exp."""
        dirs = [
            self.temp_dir / "img",
            self.exp_dir / "post",
            self.exp_dir / "img" / "head_p",
            self.exp_dir / "img" / "w-head_p",
            self.exp_dir / "img" / "post",
            self.exp_dir / "img" / "w-post",
            self.exp_dir / "img" / "av",
            self.exp_dir / "img" / "w-av",
        ]
        for d in dirs:
            try:
                d.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                logger.exception("Failed to create directory %s: %s", d, exc)
                raise

    def write_file_atomic(self, path: Path, content: str, encoding: str = "utf-8") -> None:
        """Atomically write content to path using a temporary file replacement."""
        path = Path(path)
        if path.parent and not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        with tmp.open("w", encoding=encoding) as fh:
            fh.write(content)
            fh.flush()
            try:
                os.fsync(fh.fileno())
            except Exception:
                logger.debug("fsync not supported or failed")
        tmp.replace(path)

    def append(self, temp_content: str, exp_content: Optional[str] = None, retries: int = 3) -> None:
        """Append content to temp_post and exp_post with retries on transient I/O errors."""
        if exp_content is None:
            exp_content = temp_content
        targets = [(self.temp_post, temp_content), (self.exp_post, exp_content)]
        for path, content in targets:
            attempt = 0
            while attempt < retries:
                attempt += 1
                try:
                    if path.parent and not path.parent.exists():
                        path.parent.mkdir(parents=True, exist_ok=True)
                    with path.open("a", encoding="utf-8") as fh:
                        fh.write(content + "\n")
                        fh.flush()
                        try:
                            os.fsync(fh.fileno())
                        except Exception:
                            pass
                    break
                except (OSError, IOError) as exc:
                    logger.warning("Append to %s failed (attempt %d): %s", path, attempt, exc)
                    time.sleep(0.05 * attempt)
            else:
                logger.error("Failed to append to %s after %d attempts", path, retries)
                raise IOError(f"Unable to append to {path}")

    def generate_initial_post(self, name_alea: str, high_title: str, title: str, subtitle: str, autor: str, date_str: str) -> None:
        """Render header templates for temp and exp and store footer HTML."""
        try:
            header_tmpl: Template = JINJA_ENV.get_template(constants.HEADER_TEMPLATE_FILE)
            footer_tmpl: Template = JINJA_ENV.get_template(constants.FOOTER_TEMPLATE_FILE)
        except Exception as exc:
            logger.exception("Failed to load templates: %s", exc)
            raise

        common_ctx = dict(
            high_title=high_title or "",
            title=title or "",
            subtitle=subtitle or "",
            autor=autor or "",
            date=date_str,
            name_alea=name_alea,
        )

        temp_ctx = dict(
            common_ctx,
            **{
                "bootstrap_css": "../needs/bootstrap.min.css",
                "clean_blog": "../needs/clean-blog.min.css",
                "img_path": f"img/{name_alea}head.webp",
                "jquery": "../../js/jquery/jquery.min.js",
                "bootstrap_js": "../../js/post/bootstrap.min.js",
                "clean_js": "../../js/post/clean-blog.min.js",
            },
        )

        exp_ctx = dict(
            common_ctx,
            **{
                "bootstrap_css": "../../css/post/bootstrap.min.css",
                "clean_blog": "../../css/post/clean-blog.min.css",
                "img_path": f"../../img/head_p/{name_alea}head.webp",
                "jquery": "../../js/jquery/jquery.min.js",
                "bootstrap_js": "../../js/post/bootstrap.min.js",
                "clean_js": "../../js/post/clean-blog.min.js",
            },
        )

        temp_content = header_tmpl.render(**temp_ctx)
        exp_content = header_tmpl.render(**exp_ctx)
        footer_content = footer_tmpl.render(**exp_ctx)

        # Write atomically
        self.write_file_atomic(self.temp_post, temp_content)
        self.write_file_atomic(self.exp_post, exp_content)

        self._footer_content = footer_content

    def append_footer(self) -> None:
        """Append the generated footer to both post files if not already present."""
        footer = self._footer_content
        if not footer:
            logger.info("No footer stored; skipping append_footer")
            return

        for path in (self.temp_post, self.exp_post):
            try:
                if not path.exists():
                    logger.info("Skipping footer for %s because it does not exist", path)
                    continue
                content = path.read_text(encoding="utf-8")
                if footer.strip() == "" or footer.strip() in content or content.strip().endswith("</html>") or "</footer>" in content:
                    logger.debug("Footer already present or file ends with </html> for %s; skipping", path)
                    continue
                self.append(footer, footer)
            except Exception as exc:
                logger.exception("Failed to append footer to %s: %s", path, exc)
                raise
