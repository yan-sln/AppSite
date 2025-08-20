# AppSite

A Tkinter-based desktop application for creating blog posts with a simple WYSIWYG-like workflow.
It integrates image handling, templating with Jinja2, and project file management with export capabilities.

---

## Features

* Graphical user interface built with Tkinter
* Project management with temporary (`temp/`) and export (`exp/`) directories
* Jinja2 templating with external template files in `templates/`
* Image resizing and format conversion using Pillow and python-resize-image
* Export workflow to generate a publishable static blog post
* Basic error handling and recovery dialogs
* Object-oriented architecture with clear module separation

---

## Project structure

```
appsite/
├── README.md
├── requirements.txt
├── templates/            # Jinja2 templates
│   ├── post_header.jinja
│   └── post_footer.jinja
├── needs/                # existing resources (css, js, html, etc.)
│   └── ...
├── resources/            # static assets
│   ├── favicon.ico
│   └── AppSite.png
└── src/                  # source package
    ├── __init__.py
    ├── constants.py
    ├── logging_config.py
    ├── project_files.py
    ├── popups.py
    ├── app.py
    └── main.py
```

---

## Installation

### Requirements

* Python 3.9+
* Tkinter (usually included in standard Python installations, on some Linux distributions install `python3-tk`)

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## Usage

From the project root:

```bash
python -m src.main
```

The application will launch in a windowed mode.
From the start screen you can either create a new project or open an existing one.
