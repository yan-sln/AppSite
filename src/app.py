# -*- coding: utf-8 -*-

"""Main application class that encapsulates UI, state and callbacks."""

from __future__ import annotations

import html
import os
import sys
import logging
import shutil
import time
from pathlib import Path
from typing import Optional

import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk, UnidentifiedImageError
from resizeimage import resizeimage

from .project_files import ProjectFiles
from .popups import HeaderPopup, TextPopup, ImageInfoPopup, LinkPopup, ExportNamePopup
from . import logging_config
from . import constants

logger = logging.getLogger(__name__)


def _random_name(length: int = 8) -> str:
    """Generate a small random ascii string used for filenames."""
    import random
    import string

    return "".join(random.choice(string.ascii_letters) for _ in range(length))


class App:
    """Tk application that drives the UI and uses ProjectFiles for I/O."""

    def __init__(self) -> None:
        logging_config.init_logging()
        self.project_files = ProjectFiles(auto_create=False)

        self.error_count = 0
        self.project_flag = 0
        self.dir_change_count = 0
        self.fullscreen = False

        self.root = tk.Tk()
        try:
            self.root.wm_iconbitmap(str(constants.RESOURCES_DIR / "favicon.ico"))
        except Exception:
            logger.debug("favicon missing")

        self.root.wm_title("AppSite 1.1.1")
        self.root.geometry("550x550")
        self.root.config(bg="#e3e3e3")
        self.root.attributes("-fullscreen", False)

        self.menubar = tk.Menu(self.root)
        self._build_menu()
        self._build_frames()
        self._bind_shortcuts()

        if Path(constants.EXP_DIR_NAME).exists() and Path(constants.TEMP_DIR_NAME).exists():
            self.frame_toggle(1)
        else:
            self.frame_toggle(0)

        self.root.config(menu=self.menubar)

    # ---------- UI builders ----------
    def _build_menu(self) -> None:
        file_menu = tk.Menu(self.menubar, tearoff=0)
        file_menu.add_command(label="New project", command=self.new_project)
        file_menu.add_command(label="Open", command=self.open_project)
        file_menu.add_separator()
        file_menu.add_command(label="Restart", command=self.restart)
        file_menu.add_command(label="Quit", command=self.quit)
        self.menubar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(self.menubar, tearoff=0)
        edit_menu.add_command(label="Preview", command=self.preview_web)
        edit_menu.add_command(label="Export", command=self.export)
        self.menubar.add_cascade(label="Edit", menu=edit_menu)

        help_menu = tk.Menu(self.menubar, tearoff=0)
        help_menu.add_command(label="Last modified", command=self.last_modified)
        help_menu.add_command(label="Help", command=self.help)
        self.menubar.add_cascade(label="Help", menu=help_menu)

    def _build_frames(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.elements_frame = tk.LabelFrame(self.root, text="Elements:", relief=tk.FLAT, bg="#5073FB", bd=1, fg="white")
        self.elements_frame.grid(column=0, row=0, padx=5, pady=5, sticky="EWNS", ipady=10)
        self.elements_frame.columnconfigure(0, weight=2)
        self.elements_frame.columnconfigure(1, weight=1)
        for r in range(6):
            self.elements_frame.rowconfigure(r, weight=1)

        tk.Label(self.elements_frame, text="Section title:").grid(column=0, row=0, padx=5, sticky="EWNS")
        tk.Button(self.elements_frame, text="New", command=self.section_title).grid(column=1, row=0, sticky="EWNS")
        tk.Label(self.elements_frame, text="Text:").grid(column=0, row=1, padx=5, sticky="EWNS")
        tk.Button(self.elements_frame, text="New", command=self.add_text).grid(column=1, row=1, sticky="EWNS", pady=5)
        tk.Label(self.elements_frame, text="Image:").grid(column=0, row=2, padx=5, sticky="EWNS")
        tk.Button(self.elements_frame, text="New", command=self.add_image).grid(column=1, row=2, sticky="EWNS")
        tk.Label(self.elements_frame, text="Quote:").grid(column=0, row=3, padx=5, sticky="EWNS")
        tk.Button(self.elements_frame, text="New", command=self.add_quote).grid(column=1, row=3, sticky="EWNS", pady=5)
        tk.Label(self.elements_frame, text="Link:").grid(column=0, row=4, padx=5, sticky="EWNS")
        tk.Button(self.elements_frame, text="New", command=self.add_link).grid(column=1, row=4, sticky="EWNS")
        tk.Button(self.elements_frame, text="Export", command=self.export).grid(column=0, row=5, sticky="EWNS", pady=5, padx=5)
        tk.Button(self.elements_frame, text="Preview", command=self.preview_web).grid(column=1, row=5, sticky="EWNS", pady=5)

        self.welcome_frame = tk.LabelFrame(self.root, text="", relief=tk.RIDGE, bg="#f7ef38", bd=3)
        self.welcome_frame.grid(column=0, row=0, padx=5, pady=5, sticky="EWNS")
        self.welcome_frame.columnconfigure(0, weight=1)
        self.welcome_frame.columnconfigure(1, weight=2)
        for r in range(7):
            self.welcome_frame.rowconfigure(r, weight=(9 if r == 0 else 1))

        try:
            splash = Image.open(str(constants.RESOURCES_DIR / "AppSite.png"))
            splash_photo = ImageTk.PhotoImage(splash)
            tk.Label(self.welcome_frame, image=splash_photo).grid(column=0, row=0, columnspan=2, padx=10)
            self._splash_ref = splash_photo
        except Exception:
            logger.debug("Splash image not available")

        tk.Button(self.welcome_frame, text="Help", command=self.help).grid(column=0, row=4, columnspan=2, sticky="EWNS", padx=5, pady=5)
        tk.Button(self.welcome_frame, text="Open", command=self.open_project).grid(column=0, row=5, columnspan=2, sticky="EWNS", padx=5, pady=5)
        tk.Button(self.welcome_frame, text="New Project", command=self.new_project).grid(column=0, row=6, columnspan=2, sticky="EWNS", padx=5, pady=5)

    def _bind_shortcuts(self) -> None:
        self.root.bind("<Control-F11>", self.toggle_fullscreen)
        self.root.bind("<Control-n>", lambda e=None: self.new_project())
        self.root.bind("<Control-o>", lambda e=None: self.open_project())
        self.root.bind("<Control-e>", lambda e=None: self.export())
        self.root.bind("<Control-h>", lambda e=None: self.help())
        self.root.bind("<Control-d>", lambda e=None: self.preview_web())
        self.root.bind("<Control-F12>", lambda e=None: self.quit())

    # ---------- core helpers ----------
    def _ask_for_image(self) -> Optional[str]:
        messagebox.showinfo("Help", "Select an image to start!")
        try:
            path = filedialog.askopenfilename(title="Select a file", filetypes=(("jpeg files", "*.jpg"), ("all files", "*.*")))
            return path or None
        except Exception as exc:
            logger.exception("Image dialog failed: %s", exc)
            return None

    def new_project(self) -> None:
        """Create directories and start header flow for a new project."""
        if Path(constants.EXP_DIR_NAME).exists() or Path(constants.TEMP_DIR_NAME).exists():
            if messagebox.askyesno("Existing folder", "A project already exists. Delete it?"):
                try:
                    if Path(constants.EXP_DIR_NAME).exists():
                        shutil.rmtree(constants.EXP_DIR_NAME)
                    if Path(constants.TEMP_DIR_NAME).exists():
                        shutil.rmtree(constants.TEMP_DIR_NAME)
                except Exception as exc:
                    logger.exception("Failed to remove existing project: %s", exc)
                    messagebox.showerror("Error", f"Failed removing project: {exc}")
                    return
            else:
                return

        self.project_files.ensure_dirs()
        self.header_flow()

    def open_project(self) -> None:
        """Switch to editor when a project exists."""
        if Path(constants.EXP_DIR_NAME).exists() and Path(constants.TEMP_DIR_NAME).exists():
            self.frame_toggle(1)
        else:
            messagebox.showerror("Error", "Create a project first!")

    def header_flow(self) -> None:
        """Header image selection, resize and initial post generation."""
        self.project_files.ensure_dirs()
        filename = self._ask_for_image()
        if not filename:
            return
        name = _random_name()
        try:
            with open(filename, "r+b") as fh:
                try:
                    with Image.open(fh) as img:
                        width, height = img.size
                        if width >= 1900 and height >= 600:
                            cover = resizeimage.resize_cover(img, [1900, 600])
                            cover.save(Path(constants.EXP_DIR_NAME) / "img" / "head_p" / f"{name}head.webp")
                            cover.save(Path(constants.EXP_DIR_NAME) / "img" / "w-head_p" / f"{name}head.jpg")
                            cover.save(Path(constants.TEMP_DIR_NAME) / "img" / f"{name}head.webp")
                            cover.save(Path(constants.TEMP_DIR_NAME) / "img" / f"{name}head.jpg")
                        elif width >= 950 and height >= 300:
                            cover = resizeimage.resize_cover(img, [950, 300])
                            cover.save(Path(constants.EXP_DIR_NAME) / "img" / "head_p" / f"{name}head.webp")
                            cover.save(Path(constants.EXP_DIR_NAME) / "img" / "w-head_p" / f"{name}head.jpg")
                            cover.save(Path(constants.TEMP_DIR_NAME) / "img" / f"{name}head.webp")
                            cover.save(Path(constants.TEMP_DIR_NAME) / "img" / f"{name}head.jpg")
                        else:
                            messagebox.showwarning("Too small", "Image too small for header (min 950x300).")
                            return
                except UnidentifiedImageError as exc:
                    logger.exception("Invalid image chosen: %s", exc)
                    messagebox.showerror("Image error", f"Invalid image chosen: {exc}")
                    return
        except Exception as exc:
            logger.exception("Cannot open file: %s", exc)
            messagebox.showerror("File error", f"Cannot open file: {exc}")
            return

        # optional avatar generation
        try:
            with open(filename, "r+b") as fh:
                with Image.open(fh) as img:
                    w, h = img.size
                    if w >= 306 and h >= 230:
                        cover = resizeimage.resize_cover(img, [306, 230])
                        cover.save(Path(constants.EXP_DIR_NAME) / "img" / "av" / f"{name}av.webp")
                        cover.save(Path(constants.EXP_DIR_NAME) / "img" / "w-av" / f"{name}av.jpg")
        except Exception:
            logger.debug("Avatar generation skipped")

        high_title = title = subtitle = autor = ""
        while not (high_title and title and subtitle and autor):
            dlg = HeaderPopup(self.root)
            dlg.wait()
            try:
                high_title, title, subtitle, autor = dlg.result
            except Exception:
                high_title = title = subtitle = autor = ""
            if not (high_title and title and subtitle and autor):
                if messagebox.askyesno("Empty fields", "Leave fields empty?"):
                    break

        date = time.strftime("%d/%m/%y")
        self.frame_toggle(1)
        self.project_files.generate_initial_post(name, high_title, title, subtitle, autor, date)

    def section_title(self) -> None:
        dlg = ExportNamePopup(self.root)
        dlg.wait()
        txt = dlg.result
        if not txt:
            if messagebox.askyesno("Quit", "Quit?"):
                return
            return
        _escaped = html.escape(txt)
        self.project_files.append(f'<h2 class="section-heading">{_escaped}</h2>')

    def add_image(self) -> None:
        self.project_files.ensure_dirs()
        filename = self._ask_for_image()
        if not filename:
            return
        name = _random_name()
        try:
            with open(filename, "r+b") as fh:
                try:
                    with Image.open(fh) as img:
                        width, height = img.size
                        if width >= 778 and height >= 514:
                            cover = resizeimage.resize_cover(img, [778, 514])
                            cover.save(Path(constants.EXP_DIR_NAME) / "img" / "post" / f"{name}.webp")
                            cover.save(Path(constants.EXP_DIR_NAME) / "img" / "w-post" / f"{name}.jpg")
                            cover.save(Path(constants.TEMP_DIR_NAME) / "img" / f"{name}.webp")
                            cover.save(Path(constants.TEMP_DIR_NAME) / "img" / f"{name}.jpg")
                            dlg = ImageInfoPopup(self.root)
                            dlg.wait()
                            alt, caption = dlg.result
                            alt_e = html.escape(alt)
                            caption_e = html.escape(caption)
                            temp_html = (
                                "  <a href=\"#\">\n"
                                f'    <img class="img-responsive" src="img/{name}.webp" alt="{alt_e}">\n'
                                "  </a>\n"
                                f'  <span class="caption text-muted">{caption_e}</span>\n'
                            )
                            exp_html = (
                                "  <a href=\"#\">\n"
                                f'    <img class="img-responsive" src="../../img/post/{name}.webp" alt="{alt_e}">\n'
                                "  </a>\n"
                                f'  <span class="caption text-muted">{caption_e}</span>\n'
                            )
                            self.project_files.append(temp_html, exp_html)
                        else:
                            messagebox.showwarning("Too small", "Image too small for post image (min 778x514).")
                            return
                except UnidentifiedImageError as exc:
                    logger.exception("Invalid image: %s", exc)
                    messagebox.showerror("Image error", f"Invalid image: {exc}")
        except Exception as exc:
            logger.exception("Image file open failed: %s", exc)
            messagebox.showerror("File error", f"Cannot open file: {exc}")

    def add_text(self) -> None:
        dlg = TextPopup(self.root, "Enter paragraph text")
        dlg.wait()
        txt = dlg.result
        if not txt:
            if messagebox.askyesno("Quit", "Quit?"):
                return
            return
        self.project_files.append(f"<p>{html.escape(txt)}</p>")

    def add_quote(self) -> None:
        dlg = TextPopup(self.root, "Enter quote")
        dlg.wait()
        txt = dlg.result
        if not txt:
            if messagebox.askyesno("Quit", "Quit?"):
                return
            return
        self.project_files.append(f"<blockquote>{html.escape(txt)}</blockquote>")

    def add_link(self) -> None:
        dlg = LinkPopup(self.root)
        dlg.wait()
        try:
            text, name, url = dlg.result
        except Exception:
            text = name = url = ""
        if not (text and name and url):
            if messagebox.askyesno("Empty fields", "Leave a field empty?"):
                temp_html = f'<!-- Link -->\n<p>{html.escape(text)} <a href="{html.escape(url)}">{html.escape(name)}</a>.</a></p>'
                self.project_files.append(temp_html)
                return
            if messagebox.askyesno("Quit", "Quit?"):
                return
            return
        temp_html = f'<!-- Link -->\n<p>{html.escape(text)} <a href="{html.escape(url)}">{html.escape(name)}</a>.</a></p>'
        self.project_files.append(temp_html)

    def footer(self) -> None:
        try:
            self.project_files.append_footer()
        except Exception as exc:
            logger.exception("Footer append failed: %s", exc)
            messagebox.showerror("Footer error", f"Unable to append footer: {exc}")

    # ---------- utilities ----------
    def help(self) -> None:
        try:
            path = constants.NEEDS_DIR / "aide.html"
            if path.exists():
                import webbrowser
                webbrowser.open_new_tab(str(path.resolve()))
            else:
                messagebox.showerror("Help error", "Help file not found in needs/")
        except Exception as exc:
            logger.exception("Help open failed: %s", exc)
            messagebox.showerror("Help error", f"Unable to open help: {exc}")

    def preview_web(self) -> None:
        try:
            path = Path(constants.TEMP_DIR_NAME) / "post.html"
            if path.exists():
                import webbrowser
                webbrowser.open_new_tab(str(path.resolve()))
            else:
                messagebox.showerror("Preview error", "No preview available (temp/post.html missing).")
        except Exception as exc:
            logger.exception("Preview failed: %s", exc)
            messagebox.showerror("Preview error", f"Unable to open preview: {exc}")

    def export(self) -> None:
        if not Path(constants.EXP_DIR_NAME).exists():
            messagebox.showerror("Error", "No project to export!")
            return
        if not messagebox.askyesno("Export", "This action is irreversible. Continue?"):
            return
        dlg = ExportNamePopup(self.root)
        dlg.wait()
        export_name = dlg.result
        if not export_name:
            messagebox.showerror("Missing name", "Provide a name for the exported folder.")
            return
        dest = filedialog.askdirectory(title="Select destination folder", mustexist=True, parent=self.root)
        if not dest:
            messagebox.showerror("Missing destination", "You must select a destination folder.")
            return

        # Remove temp/post.html if present and remove temp dir
        try:
            tmp_path = Path(constants.TEMP_DIR_NAME) / "post.html"
            if tmp_path.exists():
                tmp_path.unlink()
            if Path(constants.TEMP_DIR_NAME).exists():
                shutil.rmtree(constants.TEMP_DIR_NAME)
        except Exception:
            messagebox.showerror("Error", "Close any open preview and retry.")
            return

        # append footer and move export
        self.footer()
        try:
            Path(constants.EXP_DIR_NAME).rename(export_name)
        except Exception as exc:
            logger.exception("Rename exp failed: %s", exc)
            messagebox.showerror("Export error", f"Unable to rename export folder: {exc}")
            return
        try:
            shutil.move(export_name, dest)
        except Exception as exc:
            logger.exception("Move failed: %s", exc)
            messagebox.showerror("Export error", f"Unable to move exported folder: {exc}")
            return

        try:
            if Path(constants.TEMP_DIR_NAME).exists():
                shutil.rmtree(constants.TEMP_DIR_NAME)
        except Exception:
            pass

        self.frame_toggle(0)
        messagebox.showinfo("Exported", "Export completed successfully!")

    def last_modified(self) -> None:
        try:
            post_path = Path(constants.EXP_DIR_NAME) / "post" / "post.html"
            if post_path.exists():
                messagebox.showinfo("Last modified", time.ctime(post_path.stat().st_mtime))
            else:
                messagebox.showerror("Error", "No post found.")
        except Exception as exc:
            logger.exception("Last modified failed: %s", exc)
            messagebox.showerror("Error", f"Unable to retrieve modification date: {exc}")

    def frame_toggle(self, state: int) -> None:
        if state == 0:
            try:
                self.elements_frame.grid_forget()
            except Exception:
                pass
            try:
                self.welcome_frame.grid(column=0, row=0, padx=5, pady=5, sticky="EWNS")
            except Exception:
                pass
        else:
            try:
                self.elements_frame.grid(column=0, row=0, padx=5, pady=5, sticky="EWNS", ipady=10)
            except Exception:
                pass
            try:
                self.welcome_frame.grid_forget()
            except Exception:
                pass

    def restart(self) -> None:
        if not messagebox.askyesno("Restart", "Are you sure you want to restart the application?"):
            return
        try:
            try:
                self.root.destroy()
            except Exception:
                try:
                    self.root.quit()
                except Exception:
                    pass
            try:
                sys.stdout.flush()
                sys.stderr.flush()
            except Exception:
                pass
            python_exe = sys.executable or "python"
            args = [python_exe] + sys.argv
            os.execv(python_exe, args)
        except Exception as exc:
            logger.exception("Restart failed: %s", exc)
            messagebox.showerror("Restart error", f"Unable to restart the application: {exc}")

    def quit(self) -> None:
        if messagebox.askyesno("Quit", "Are you sure you want to quit the application?"):
            try:
                self.root.destroy()
            except Exception:
                try:
                    self.root.quit()
                except Exception:
                    pass

    def toggle_fullscreen(self, event: Optional[object] = None) -> None:
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)

    def run(self) -> None:
        """Start Tk mainloop."""
        try:
            self.root.mainloop()
        except Exception as exc:
            logger.exception("Mainloop crashed: %s", exc)
            try:
                messagebox.showerror("Fatal error", f"The UI crashed: {exc}")
            except Exception:
                pass
