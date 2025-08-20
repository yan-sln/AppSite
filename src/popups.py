# -*- coding: utf-8 -*-

"""Modal tkinter popups used by the App."""

from __future__ import annotations

import logging
from typing import Optional, Tuple

import tkinter as tk
from tkinter import messagebox

logger = logging.getLogger(__name__)


class BasePopup:
    """Base class for modal popup dialogs."""

    def __init__(self, parent: tk.Tk, title: str, help_text: Optional[str] = None) -> None:
        self.top = tk.Toplevel(parent)
        self.top.wm_title(title)
        if help_text:
            try:
                messagebox.showinfo(title, help_text)
            except Exception:
                logger.debug("Unable to show help messagebox")
        self.top.config(bg="#e3e3e3")

    def wait(self) -> None:
        """Block until popup is destroyed."""
        self.top.wait_window(self.top)


class TextPopup(BasePopup):
    """Popup for multiline text."""

    def __init__(self, parent: tk.Tk, help_text: str = "Enter text") -> None:
        super().__init__(parent, "Text Input", help_text)
        self.result: str = ""
        self.top.geometry("350x475")
        self.top.columnconfigure(0, weight=1)
        self.top.rowconfigure(0, weight=3)
        self.top.rowconfigure(1, weight=1)

        self.textbox = tk.Text(self.top, width=70)
        self.textbox.grid(column=0, row=0, padx=5, pady=5, sticky="EWNS", ipady=10)
        submit = tk.Button(self.top, text="Ok", command=self._on_submit)
        submit.grid(column=0, row=1, padx=5, pady=5, sticky="EWNS")

    def _on_submit(self) -> None:
        try:
            self.result = self.textbox.get(1.0, tk.END + "-1c")
        except Exception as exc:
            logger.exception("Failed to read text from popup: %s", exc)
            self.result = ""
        finally:
            self.top.destroy()


class HeaderPopup(BasePopup):
    """Popup for header metadata (high_title, title, subtitle, author)."""

    def __init__(self, parent: tk.Tk, help_text: str = "Enter header data") -> None:
        super().__init__(parent, "Header", help_text)
        self.result: Tuple[str, str, str, str] = ("", "", "", "")
        self.top.geometry("350x475")
        self.top.columnconfigure(0, weight=1)
        self.top.columnconfigure(1, weight=3)
        for i in range(5):
            self.top.rowconfigure(i, weight=1)

        tk.Label(self.top, text="Header title (date ok): ").grid(column=0, row=0, padx=5, pady=5, sticky="EWNS")
        self.entry_high = tk.Entry(self.top)
        self.entry_high.grid(column=1, row=0, padx=5, pady=5)

        tk.Label(self.top, text="Post title: ").grid(column=0, row=1, padx=5, pady=5, sticky="EWNS")
        self.entry_title = tk.Entry(self.top)
        self.entry_title.grid(column=1, row=1, padx=5, pady=5)

        tk.Label(self.top, text="Post subtitle: ").grid(column=0, row=2, padx=5, pady=5, sticky="EWNS")
        self.entry_sub = tk.Entry(self.top)
        self.entry_sub.grid(column=1, row=2, padx=5, pady=5)

        tk.Label(self.top, text="Author: ").grid(column=0, row=3, padx=5, pady=5, sticky="EWNS")
        self.entry_author = tk.Entry(self.top)
        self.entry_author.grid(column=1, row=3, padx=5, pady=5)

        submit = tk.Button(self.top, text="Ok", command=self._on_submit)
        submit.grid(column=0, row=4, columnspan=2, padx=5, pady=5, sticky="EWNS")

    def _on_submit(self) -> None:
        try:
            self.result = (self.entry_high.get(), self.entry_title.get(), self.entry_sub.get(), self.entry_author.get())
        except Exception as exc:
            logger.exception("Header popup read failed: %s", exc)
            self.result = ("", "", "", "")
        finally:
            self.top.destroy()


class ImageInfoPopup(BasePopup):
    """Popup for image alt text and caption."""

    def __init__(self, parent: tk.Tk, help_text: str = "Enter image descriptions") -> None:
        super().__init__(parent, "Image Info", help_text)
        self.result: Tuple[str, str] = ("", "")
        self.top.geometry("450x375")
        self.top.columnconfigure(0, weight=1)
        self.top.columnconfigure(1, weight=3)
        for i in range(3):
            self.top.rowconfigure(i, weight=1)

        tk.Label(self.top, text="Short description (alt): ").grid(column=0, row=0, padx=5, pady=5, sticky="EWNS")
        self.entry_alt = tk.Entry(self.top)
        self.entry_alt.grid(column=1, row=0, padx=5, pady=5)

        tk.Label(self.top, text="Visible description (caption): ").grid(column=0, row=1, padx=5, pady=5, sticky="EWNS")
        self.entry_caption = tk.Entry(self.top)
        self.entry_caption.grid(column=1, row=1, padx=5, pady=5)

        submit = tk.Button(self.top, text="Ok", command=self._on_submit)
        submit.grid(column=0, row=2, columnspan=2, padx=5, pady=5, sticky="EWNS")

    def _on_submit(self) -> None:
        try:
            self.result = (self.entry_alt.get(), self.entry_caption.get())
        except Exception as exc:
            logger.exception("ImageInfo popup read failed: %s", exc)
            self.result = ("", "")
        finally:
            self.top.destroy()


class LinkPopup(BasePopup):
    """Popup for link content: text, name and url."""

    def __init__(self, parent: tk.Tk, help_text: str = "Enter link information") -> None:
        super().__init__(parent, "Link", help_text)
        self.result: Tuple[str, str, str] = ("", "", "")
        self.top.geometry("350x475")
        self.top.columnconfigure(0, weight=1)
        self.top.columnconfigure(1, weight=3)
        for i in range(5):
            self.top.rowconfigure(i, weight=1)

        tk.Label(self.top, text="Text: ").grid(column=0, row=0, padx=5, pady=5, sticky="EWNS")
        self.entry_text = tk.Entry(self.top)
        self.entry_text.grid(column=1, row=0, padx=5, pady=5)

        tk.Label(self.top, text="Link name (required): ").grid(column=0, row=1, padx=5, pady=5, sticky="EWNS")
        self.entry_name = tk.Entry(self.top)
        self.entry_name.grid(column=1, row=1, padx=5, pady=5)

        tk.Label(self.top, text="URL: ").grid(column=0, row=2, padx=5, pady=5, sticky="EWNS")
        self.entry_url = tk.Entry(self.top)
        self.entry_url.grid(column=1, row=2, padx=5, pady=5)

        submit = tk.Button(self.top, text="Ok", command=self._on_submit)
        submit.grid(column=0, row=4, columnspan=2, padx=5, pady=5, sticky="EWNS")

    def _on_submit(self) -> None:
        try:
            self.result = (self.entry_text.get(), self.entry_name.get(), self.entry_url.get())
        except Exception as exc:
            logger.exception("Link popup read failed: %s", exc)
            self.result = ("", "", "")
        finally:
            self.top.destroy()


class ExportNamePopup(BasePopup):
    """Popup to ask for an export folder name."""

    def __init__(self, parent: tk.Tk, help_text: str = "Enter export folder name") -> None:
        super().__init__(parent, "Export name", help_text)
        self.result: str = ""
        self.top.geometry("300x150")
        self.top.columnconfigure(0, weight=1)
        self.top.columnconfigure(1, weight=1)
        for i in range(2):
            self.top.rowconfigure(i, weight=1)

        tk.Label(self.top, text="Enter name: ").grid(column=0, row=0, padx=5, pady=5, sticky="EWNS")
        self.entry = tk.Entry(self.top)
        self.entry.grid(column=1, row=0, padx=5, pady=5)

        submit = tk.Button(self.top, text="Ok", command=self._on_submit)
        submit.grid(column=0, row=1, columnspan=2, padx=5, pady=5, sticky="EWNS")

    def _on_submit(self) -> None:
        try:
            self.result = self.entry.get()
        except Exception as exc:
            logger.exception("ExportName popup read failed: %s", exc)
            self.result = ""
        finally:
            self.top.destroy()
