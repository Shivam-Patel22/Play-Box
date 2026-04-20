# 10 — Error Handling & Validation Specification

---

## Philosophy

- **Never crash silently** — all exceptions must be caught and shown to user via `messagebox`
- **Validate early** — check inputs before hitting the database
- **Parameterised queries always** — no string interpolation in SQL
- **Meaningful messages** — errors tell the user what to fix, not just "error occurred"

---

## Global Exception Handler

Add to `main.py` to catch any unhandled exceptions:

```python
import traceback
from tkinter import messagebox

def handle_unexpected_error(exc_type, exc_value, exc_tb):
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    messagebox.showerror(
        "Unexpected Error",
        f"An unexpected error occurred. Please restart the app.\n\n{exc_value}"
    )
    # Optional: log to file
    with open("error.log", "a") as f:
        f.write(f"\n{'='*60}\n{error_msg}")

import sys
sys.excepthook = handle_unexpected_error
```

---

## Database Error Handling

Wrap all DB calls that could fail:

```python
import sqlite3

def safe_db_call(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed: users.email" in str(e):
            raise ValueError("An account with this email already exists.")
        raise ValueError(f"Database constraint error: {e}")
    except sqlite3.OperationalError as e:
        raise RuntimeError(f"Database error: {e}")
```

### Specific DB Error Cases

| Situation | Exception | User Message |
|-----------|-----------|-------------|
| Duplicate email signup | `sqlite3.IntegrityError` | "An account with this email already exists." |
| Duplicate payment | `sqlite3.IntegrityError` | "Payment already recorded for this booking." |
| DB file locked | `sqlite3.OperationalError` | "Database is busy. Please try again." |
| Connection failure | `sqlite3.OperationalError` | "Could not connect to database. Check app installation." |

---

## Auth Validation Errors

All returned by `auth.validate_signup_fields()` as a list:

```python
VALIDATION_MESSAGES = {
    "name_empty"    : "Full Name is required.",
    "name_short"    : "Full Name must be at least 2 characters.",
    "name_long"     : "Full Name cannot exceed 80 characters.",
    "name_invalid"  : "Full Name can only contain letters and spaces.",
    "email_empty"   : "Email address is required.",
    "email_invalid" : "Please enter a valid email address.",
    "phone_empty"   : "Phone number is required.",
    "phone_invalid" : "Phone number must be exactly 10 digits.",
    "pw_empty"      : "Password is required.",
    "pw_short"      : "Password must be at least 6 characters.",
    "pw_no_upper"   : "Password must contain at least one uppercase letter.",
    "pw_no_digit"   : "Password must contain at least one digit.",
    "pw_mismatch"   : "Passwords do not match.",
    "role_invalid"  : "Please select a valid role (Customer or Turf Owner).",
    "email_taken"   : "An account with this email already exists.",
}
```

Login errors:
```python
LOGIN_ERRORS = {
    "email_empty"   : "Please enter your email address.",
    "pw_empty"      : "Please enter your password.",
    "invalid_creds" : "Invalid email or password.",
}
```

---

## Booking Validation Errors

Checked in `BookingDialog.on_confirm()`:

| Check | Error Message |
|-------|---------------|
| end_time <= start_time | "End time must be after start time." |
| Duration < 30 minutes | "Minimum booking duration is 30 minutes." |
| Date in the past | "Cannot book a turf for a past date." |
| No slots available | "No slots available for this turf. Please choose another." |
| Time slot conflict | "This time slot is already booked. Please choose a different time." |
| Turf inactive | "This turf is no longer available." |

```python
def validate_booking(turf, booking_date, start_time, end_time) -> list[str]:
    errors = []
    import datetime

    # Date check
    today = datetime.date.today().isoformat()
    if booking_date < today:
        errors.append("Cannot book a turf for a past date.")

    # Time check
    from utils import time_to_minutes
    start_m = time_to_minutes(start_time)
    end_m   = time_to_minutes(end_time)
    if end_m <= start_m:
        errors.append("End time must be after start time.")
    elif (end_m - start_m) < 30:
        errors.append("Minimum booking duration is 30 minutes.")

    # Slots check
    if turf["available_slots"] <= 0:
        errors.append("No slots available for this turf.")

    # Conflict check (only if no other errors)
    if not errors:
        import database
        if database.check_slot_conflict(turf["id"], booking_date, start_time, end_time):
            errors.append("This time slot is already booked. Please choose a different time.")

    return errors
```

---

## Turf Form Validation Errors

Returned by `AddTurfTab.validate_turf_fields()`:

| Field | Check | Message |
|-------|-------|---------|
| name | empty | "Turf Name is required." |
| name | < 3 chars | "Turf Name must be at least 3 characters." |
| name | > 100 chars | "Turf Name cannot exceed 100 characters." |
| sport | not in list | "Please select a valid sport from the dropdown." |
| area | empty | "Area is required." |
| location | empty | "Location / Address is required." |
| price | empty | "Price per hour is required." |
| price | not a number | "Price must be a valid number (e.g., 500 or 750.50)." |
| price | <= 0 | "Price must be greater than zero." |
| slots | empty | "Number of slots is required." |
| slots | not integer | "Slots must be a whole number." |
| slots | < 1 or > 50 | "Slots must be between 1 and 50." |

---

## Payment Validation Errors

Returned by `PaymentDialog.validate_payment_fields(method)`:

### UPI
```python
if not upi_id:
    errors.append("UPI ID is required.")
elif not utils.is_valid_upi(upi_id):
    errors.append("Invalid UPI ID format. Example: name@upi")
```

### Credit / Debit Card
```python
if not cardholder_name.strip():
    errors.append("Cardholder name is required.")
if not utils.is_valid_card_number(card_number):
    errors.append("Card number must be exactly 16 digits.")
if not utils.is_valid_expiry(expiry):
    errors.append("Invalid or expired card expiry. Format: MM/YY")
if not utils.is_valid_cvv(cvv):
    errors.append("CVV must be exactly 3 digits.")
```

### Net Banking
```python
if not bank_var.get():
    errors.append("Please select a bank.")
if not account_number.strip() or not account_number.isdigit():
    errors.append("Please enter a valid account number (digits only).")
if not utils.is_valid_ifsc(ifsc):
    errors.append("Invalid IFSC code. Format: ABCD0123456")
```

---

## Admin Action Validations

### Accept Booking
```python
if booking["status"] != "Pending":
    messagebox.showerror("Cannot Accept",
        f"This booking is already '{booking['status']}' and cannot be accepted.")
    return
```

### Reject Booking
```python
if booking["status"] != "Pending":
    messagebox.showerror("Cannot Reject",
        f"Only Pending bookings can be rejected. Current status: {booking['status']}.")
    return
```

### Delete Turf
```python
# Check for active (Pending/Confirmed) bookings
active = [b for b in database.get_bookings_by_owner(session.get_user_id())
          if b["turf_id"] == turf_id and b["status"] in ("Pending", "Confirmed")]
if active:
    if not messagebox.askyesno(
        "Bookings Exist",
        f"This turf has {len(active)} active booking(s). "
        "Deleting will hide the turf but existing bookings remain. Continue?"
    ):
        return
```

---

## Treeview Empty State

When no data is available in a Treeview, show a placeholder:

```python
def show_empty_state(tree: ttk.Treeview, message: str):
    """Insert a single disabled row with a placeholder message."""
    tree.insert("", "end", values=(message,) + ("",) * (len(tree["columns"]) - 1),
                tags=("empty",))
    tree.tag_configure("empty", foreground="#aaaaaa", font=("Arial", 11, "italic"))
```

Usage:
```python
bookings = database.get_bookings_by_customer(session.get_user_id())
if not bookings:
    show_empty_state(tree, "No bookings found. Browse turfs to make your first booking!")
```

---

## No Search Results State

When `search_turfs()` returns empty:

```python
def render_turf_cards(results):
    utils.clear_frame(scroll_frame)
    if not results:
        no_result = tk.Frame(scroll_frame, bg="#f5f5f5")
        no_result.pack(expand=True, pady=60)
        tk.Label(no_result, text="😕", font=("Arial", 40), bg="#f5f5f5").pack()
        tk.Label(no_result, text="No turfs found.",
                 font=("Arial", 16, "bold"), fg="#333", bg="#f5f5f5").pack(pady=8)
        tk.Label(no_result, text="Try changing the sport or area filter.",
                 font=("Arial", 11), fg="#888", bg="#f5f5f5").pack()
        return
    # ... render cards normally
```

---

## Logging

For debugging, add a simple file logger:

```python
# utils.py
import logging

logging.basicConfig(
    filename="turfbook.log",
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def log_error(context: str, error: Exception):
    logging.error(f"{context}: {type(error).__name__}: {error}")
```

Use in all database functions:
```python
try:
    # DB operation
except Exception as e:
    utils.log_error("create_booking", e)
    raise
```
