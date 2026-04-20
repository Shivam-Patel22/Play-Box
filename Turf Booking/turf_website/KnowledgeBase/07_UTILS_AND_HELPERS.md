# 07 — Utils & Helper Functions Specification
## File: `utils.py`

---

## Full `utils.py` Implementation

```python
"""
utils.py — Shared utility functions for TurfBook Pro
"""

import tkinter as tk
from tkinter import ttk
import random
import string
import datetime
import re


# ─── Window Helpers ─────────────────────────────────────────────────────────

def center_window(window: tk.Toplevel | tk.Tk, width: int, height: int) -> None:
    """
    Center a Tkinter window on the screen.
    Call AFTER window.update_idletasks() if the window has been shown.
    """
    window.update_idletasks()
    sw = window.winfo_screenwidth()
    sh = window.winfo_screenheight()
    x  = (sw - width)  // 2
    y  = (sh - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")


def disable_close(window: tk.Toplevel) -> None:
    """
    Prevent the user from closing a Toplevel window via the [X] button.
    Used during processing popups.
    """
    window.protocol("WM_DELETE_WINDOW", lambda: None)


# ─── Security ────────────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    """Return SHA-256 hex digest of a plain-text password."""
    import hashlib
    return hashlib.sha256(plain.encode("utf-8")).hexdigest()


def verify_password(plain: str, stored_hash: str) -> bool:
    """Return True if SHA-256(plain) == stored_hash."""
    return hash_password(plain) == stored_hash


# ─── ID / Reference Generation ───────────────────────────────────────────────

def generate_transaction_id() -> str:
    """
    Generate a unique payment transaction ID.
    Format: TXN + 12 uppercase alphanumeric chars
    Example: TXNA3K9ZBQ2PXN4
    """
    chars = string.ascii_uppercase + string.digits
    return "TXN" + "".join(random.choices(chars, k=12))


# ─── Validation Helpers ───────────────────────────────────────────────────────

def is_valid_email(email: str) -> bool:
    """Return True if email matches basic RFC pattern."""
    pattern = r'^[\w\.\-]+@[\w\.\-]+\.\w{2,}$'
    return bool(re.match(pattern, email.strip()))


def is_valid_phone(phone: str) -> bool:
    """Return True if phone is exactly 10 digits."""
    return bool(re.match(r'^\d{10}$', phone.strip()))


def is_strong_password(password: str) -> bool:
    """
    Return True if password meets requirements:
    - Minimum 6 characters
    - At least 1 uppercase letter
    - At least 1 digit
    """
    if len(password) < 6:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    return True


def is_valid_upi(upi_id: str) -> bool:
    """Validate UPI ID format: localpart@bankhandle"""
    return bool(re.match(r'^[\w.\-]+@[\w]+$', upi_id.strip()))


def is_valid_ifsc(ifsc: str) -> bool:
    """IFSC: 4 uppercase letters, '0', 6 alphanumeric chars."""
    return bool(re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', ifsc.strip()))


def is_valid_card_number(number: str) -> bool:
    """Return True if card number is exactly 16 digits."""
    return bool(re.match(r'^\d{16}$', number.replace(" ", "")))


def is_valid_cvv(cvv: str) -> bool:
    """Return True if CVV is exactly 3 digits."""
    return bool(re.match(r'^\d{3}$', cvv.strip()))


def is_valid_expiry(expiry: str) -> bool:
    """
    Validate MM/YY format and ensure the card is not expired.
    """
    if not re.match(r'^\d{2}/\d{2}$', expiry.strip()):
        return False
    mm, yy = expiry.split("/")
    month, year = int(mm), int("20" + yy)
    now = datetime.date.today()
    exp_date = datetime.date(year, month, 1)
    return exp_date >= datetime.date(now.year, now.month, 1)


# ─── Time / Date Helpers ──────────────────────────────────────────────────────

def time_to_minutes(time_str: str) -> int:
    """
    Convert "HH:MM" string to total minutes from midnight.
    E.g., "08:30" → 510
    """
    h, m = map(int, time_str.split(":"))
    return h * 60 + m


def minutes_to_time(minutes: int) -> str:
    """
    Convert total minutes to "HH:MM" string.
    E.g., 510 → "08:30"
    """
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def calculate_duration_hours(start_time: str, end_time: str) -> float:
    """
    Return duration in hours between two "HH:MM" strings.
    Returns 0.0 if end <= start.
    """
    start = time_to_minutes(start_time)
    end   = time_to_minutes(end_time)
    if end <= start:
        return 0.0
    return (end - start) / 60.0


def calculate_price(price_per_hour: float, start_time: str, end_time: str) -> float:
    """Return total price for a booking given rate and time window."""
    return price_per_hour * calculate_duration_hours(start_time, end_time)


def format_currency(amount: float) -> str:
    """Return amount formatted as Indian Rupee string. E.g., 1400.0 → '₹1,400.00'"""
    return f"₹{amount:,.2f}"


def format_date_display(date_str: str) -> str:
    """
    Convert "YYYY-MM-DD" to "DD Mon YYYY" for display.
    E.g., "2025-04-10" → "10 Apr 2025"
    """
    try:
        d = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return d.strftime("%d %b %Y")
    except ValueError:
        return date_str


def format_time_range(start_time: str, end_time: str) -> str:
    """Return "08:00 – 10:00" formatted string."""
    return f"{start_time} – {end_time}"


def get_current_datetime_str() -> str:
    """Return current datetime as "YYYY-MM-DD HH:MM:SS"."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ─── UI Helpers ──────────────────────────────────────────────────────────────

def add_placeholder(entry: ttk.Entry, placeholder: str,
                    fg_default: str = "#aaaaaa",
                    fg_active: str  = "#333333") -> None:
    """
    Add placeholder text behaviour to a ttk.Entry.
    Clears on focus-in, restores on focus-out if empty.
    """
    entry.insert(0, placeholder)
    entry.config(foreground=fg_default)

    def on_focus_in(event):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(foreground=fg_active)

    def on_focus_out(event):
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(foreground=fg_default)

    entry.bind("<FocusIn>",  on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)


def make_scrollable_frame(parent: tk.Widget) -> tuple[tk.Frame, tk.Frame, tk.Canvas]:
    """
    Create a vertically scrollable frame.
    Returns (outer_frame, inner_frame, canvas).
    Pack or grid outer_frame in the parent.
    Add children to inner_frame.
    """
    outer = tk.Frame(parent, bg="#f5f5f5")
    canvas = tk.Canvas(outer, bg="#f5f5f5", highlightthickness=0)
    scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    inner = tk.Frame(canvas, bg="#f5f5f5")

    inner.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=inner, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left",  fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Cross-platform mouse wheel
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
    canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll( 1, "units"))

    return outer, inner, canvas


def clear_frame(frame: tk.Frame) -> None:
    """Destroy all children of a frame (used before re-rendering cards)."""
    for widget in frame.winfo_children():
        widget.destroy()


def show_loading_label(parent: tk.Frame, text: str = "Loading...") -> tk.Label:
    """
    Show a temporary loading label in the center of parent.
    Call .destroy() on the returned label when done.
    """
    lbl = tk.Label(parent, text=text,
                   font=("Arial", 13), fg="#888888", bg="#f5f5f5")
    lbl.pack(expand=True)
    return lbl


def make_separator(parent: tk.Widget, color: str = "#e0e0e0",
                   pady: int = 8) -> tk.Frame:
    """Return a thin horizontal line Frame acting as a separator."""
    line = tk.Frame(parent, bg=color, height=1)
    line.pack(fill="x", pady=pady)
    return line


# ─── Sport Helpers ────────────────────────────────────────────────────────────

SPORT_EMOJI = {
    "Cricket":    "🏏",
    "Football":   "⚽",
    "Pickleball": "🏓",
    "Pool":       "🎱",
    "Snooker":    "🎯",
}

SPORT_BADGE_COLORS = {
    "Cricket":    ("#2e7d32", "#ffffff"),
    "Football":   ("#1565c0", "#ffffff"),
    "Pickleball": ("#e65100", "#ffffff"),
    "Pool":       ("#4a148c", "#ffffff"),
    "Snooker":    ("#880e4f", "#ffffff"),
}

SPORTS_LIST = ["Cricket", "Football", "Pickleball", "Pool", "Snooker"]


def get_sport_emoji(sport: str) -> str:
    """Return emoji for sport, fallback to '🏅'."""
    return SPORT_EMOJI.get(sport, "🏅")


def get_sport_badge_colors(sport: str) -> tuple[str, str]:
    """Return (bg_color, text_color) for sport badge."""
    return SPORT_BADGE_COLORS.get(sport, ("#9e9e9e", "#ffffff"))
```

---

## Helper Usage Examples

```python
# In booking.py:
price = utils.calculate_price(turf["price_per_hour"], "08:00", "10:00")
display = utils.format_currency(price)   # → "₹1,400.00"

# In payment.py:
txn_id = utils.generate_transaction_id()   # → "TXNA3K9ZBQ2PXN4"

# In auth.py:
h = utils.hash_password("MyPass1")
ok = utils.verify_password("MyPass1", h)  # → True

# In search.py:
emoji = utils.get_sport_emoji("Football")         # → "⚽"
bg, fg = utils.get_sport_badge_colors("Football") # → ("#1565c0","#ffffff")
```
