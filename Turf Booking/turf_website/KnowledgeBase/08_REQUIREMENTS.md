# 08 — Requirements & Installation Specification

---

## `requirements.txt`

```
tkcalendar==1.6.1
matplotlib==3.8.4
Pillow==10.3.0
```

> **Note:** `tkinter`, `sqlite3`, `hashlib`, `re`, `datetime`, `random`, `string`, `os`, `subprocess`, `sys` are all Python standard library modules — **no installation needed**.

---

## Python Version

```
Python >= 3.10  (required for modern type hint syntax: X | Y, list[X])
Python 3.11 or 3.12 recommended for best compatibility
```

---

## Platform Support

| Platform | Status |
|----------|--------|
| Windows 10/11 | ✅ Fully supported |
| macOS 12+ | ✅ Fully supported |
| Ubuntu 20.04+ | ✅ Fully supported (install python3-tk separately) |

---

## Installation Instructions

### Step 1 — Clone / Download Project
```bash
# If using git:
git clone https://github.com/yourrepo/turf_booking.git
cd turf_booking

# Or download ZIP and extract, then navigate to folder
```

### Step 2 — Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Linux Only: Install Tkinter
```bash
# Ubuntu / Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter
```

### Step 5 — Run the App
```bash
python main.py
```

The database file `turf_booking.db` will be **automatically created** on first run with demo data.

---

## Demo Credentials (Auto-Seeded)

| Role | Email | Password |
|------|-------|----------|
| Admin (Turf Owner) | admin@turfbook.com | Admin@123 |
| Customer | user@turfbook.com | User@123 |

---

## Package Explanations

### `tkcalendar`
- Provides `Calendar` and `DateEntry` widgets for Tkinter
- Used in: Booking dialog for date picker
- Install: `pip install tkcalendar`
- Import: `from tkcalendar import Calendar`

### `matplotlib`
- Industry-standard data visualization library
- Used in: Admin Revenue tab — bar chart of revenue per turf
- Only `Figure` and `FigureCanvasTkAgg` backend used
- Install: `pip install matplotlib`
- Import:
  ```python
  from matplotlib.figure import Figure
  from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
  ```

### `Pillow (PIL)`
- Image processing library
- Used in: Turf image preview in Add Turf form, turf card image display
- Install: `pip install Pillow`
- Import:
  ```python
  from PIL import Image, ImageTk
  ```

---

## `setup.py` (Optional — for packaging)

```python
from setuptools import setup, find_packages

setup(
    name="TurfBookPro",
    version="1.0.0",
    author="Your Name",
    description="Turf Booking Desktop App",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "tkcalendar>=1.6.1",
        "matplotlib>=3.8.0",
        "Pillow>=10.0.0",
    ],
    entry_points={
        "console_scripts": [
            "turfbook=main:main",
        ]
    },
)
```

---

## Common Installation Errors

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: No module named 'tkinter'` | On Linux: `sudo apt-get install python3-tk` |
| `ModuleNotFoundError: No module named 'tkcalendar'` | Run `pip install tkcalendar` |
| `ModuleNotFoundError: No module named 'PIL'` | Run `pip install Pillow` (not `PIL`) |
| `ModuleNotFoundError: No module named 'matplotlib'` | Run `pip install matplotlib` |
| `sqlite3.OperationalError: unable to open database file` | Ensure you run `python main.py` from the project root directory |
| `_tkinter.TclError: bitmap not defined` | Image file path is wrong or missing — check `assets/` folder |
