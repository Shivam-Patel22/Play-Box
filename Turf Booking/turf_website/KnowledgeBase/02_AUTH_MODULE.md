# 02 — Authentication Module Specification
## Files: `auth.py` · `session.py` · `main.py`

---

## `session.py` — Global Session State

```python
# session.py
# Single source of truth for logged-in user.
# Import this module wherever you need current user context.

_current_user: dict | None = None

def set_user(user_row) -> None:
    """
    Store logged-in user. Call after successful login.
    user_row is a sqlite3.Row from users table.
    Converts to plain dict for easy key access.
    """
    global _current_user
    _current_user = dict(user_row)

def get_user() -> dict | None:
    """Return current user dict or None if not logged in."""
    return _current_user

def get_user_id() -> int | None:
    return _current_user["id"] if _current_user else None

def get_role() -> str | None:
    return _current_user["role"] if _current_user else None

def clear() -> None:
    """Call on logout."""
    global _current_user
    _current_user = None
```

---

## `auth.py` — Business Logic

```python
import hashlib
import re

def hash_password(plain: str) -> str:
    """Return SHA-256 hex digest of plain password."""
    return hashlib.sha256(plain.encode()).hexdigest()

def verify_password(plain: str, stored_hash: str) -> bool:
    """Return True if SHA-256(plain) matches stored_hash."""
    return hash_password(plain) == stored_hash

def validate_signup_fields(full_name, email, phone, password, confirm_password, role) -> list[str]:
    """
    Run all field validations.
    Return list of error strings (empty list = all valid).

    Rules:
    - full_name  : non-empty, 2-80 chars, letters and spaces only
    - email      : valid format (regex), non-empty
    - phone      : exactly 10 digits
    - password   : min 6 chars, at least 1 uppercase, 1 digit
    - confirm_pw : must match password
    - role       : must be 'customer' or 'admin'
    """

def validate_login_fields(email, password) -> list[str]:
    """
    Validate login inputs.
    Rules:
    - email    : non-empty
    - password : non-empty
    """

def do_signup(full_name, email, phone, password, confirm_password, role) -> tuple[bool, str]:
    """
    Full signup flow.
    1. validate_signup_fields
    2. Check email not already taken (database.get_user_by_email)
    3. hash_password
    4. database.create_user
    Returns (True, "Account created successfully!") on success,
            (False, "error message") on failure.
    """

def do_login(email, password) -> tuple[bool, str]:
    """
    Full login flow.
    1. validate_login_fields
    2. database.get_user_by_email
    3. verify_password
    4. session.set_user
    Returns (True, "Login successful!") on success,
            (False, "Invalid email or password.") on failure.
    """
```

---

## `main.py` — Application Entry Point

```python
"""
main.py — Entry point for TurfBook Pro

Responsibilities:
1. Call database.initialize_database()
2. Call database.seed_demo_data()
3. Create the root Tk window (hidden)
4. Launch AuthWindow
5. On successful login, destroy AuthWindow and open correct dashboard
6. Start mainloop()
"""
```

---

## AuthWindow — Tkinter UI Specification

### Window Properties
```
Title       : TurfBook Pro — Login
Size        : 500 × 600  (fixed, not resizable)
Position    : Centered on screen (use utils.center_window)
Background  : #1a472a  (dark green)
```

### Layout — Two Frames Toggled

The Auth window uses a single `Tk()` root. Two inner frames are stacked:
- `LoginFrame`  — shown first
- `SignupFrame` — shown when user clicks "Create Account"

Use `.pack_forget()` / `.pack()` to toggle between them.

---

### LoginFrame Layout

```
┌─────────────────────────────────────────┐
│                                         │
│          [Logo Image — 80×80]           │
│        TurfBook Pro  (title text)       │
│       Book Your Game, Own Your Turf     │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Email Address                  │   │
│  │  [________________________]     │   │
│  │                                 │   │
│  │  Password                       │   │
│  │  [________________________] 👁  │   │
│  │                                 │   │
│  │     [ LOGIN  (full-width btn) ] │   │
│  │                                 │   │
│  │   Don't have an account?        │   │
│  │   [Create Account] (link style) │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

#### Widget Details
| Widget | Type | Style / Notes |
|--------|------|---------------|
| Logo | `Label` with `PhotoImage` | 80×80 px, fallback to "🏟️" emoji text if no image |
| App title | `Label` | font=("Arial",22,"bold"), fg=#f0a500 |
| Tagline | `Label` | font=("Arial",10), fg=#c8e6c9 |
| Card frame | `Frame` | bg=#ffffff, padx=30, pady=30, relief=flat |
| Field labels | `Label` | font=("Arial",10,"bold"), fg=#333333 |
| Email entry | `ttk.Entry` | width=35 |
| Password entry | `ttk.Entry` | show="●", width=33 |
| Show/hide password | `Button` | text="👁", bg=#ffffff, borderwidth=0, toggles show="" / show="●" |
| Login button | `Button` | bg=#1a472a, fg=#ffffff, font bold, width=30, padx=10, pady=8, cursor=hand2 |
| Create Account | `Label` | fg=#1a472a, cursor=hand2, underline on hover, calls toggle_to_signup() |

#### Login Button Click — `on_login_click()`
```python
def on_login_click():
    email    = email_var.get().strip()
    password = pw_var.get()
    success, message = auth.do_login(email, password)
    if success:
        role = session.get_role()
        root.destroy()             # close auth window
        if role == "customer":
            open_customer_dashboard()
        else:
            open_admin_dashboard()
    else:
        messagebox.showerror("Login Failed", message)
```

---

### SignupFrame Layout

```
┌─────────────────────────────────────────┐
│         Create Your Account             │
│         Join TurfBook Pro Today         │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Full Name                      │   │
│  │  [________________________]     │   │
│  │  Email Address                  │   │
│  │  [________________________]     │   │
│  │  Phone Number                   │   │
│  │  [________________________]     │   │
│  │  Password                       │   │
│  │  [________________________]     │   │
│  │  Confirm Password               │   │
│  │  [________________________]     │   │
│  │  I am a:                        │   │
│  │  ◉ Customer  ○ Turf Owner       │   │
│  │                                 │   │
│  │  [ CREATE ACCOUNT (full-width)] │   │
│  │                                 │   │
│  │   Already have an account?      │   │
│  │   [Login Here]  (link style)    │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

#### Signup Button Click — `on_signup_click()`
```python
def on_signup_click():
    # Gather all field values
    success, message = auth.do_signup(
        full_name, email, phone, password, confirm_password, role
    )
    if success:
        messagebox.showinfo("Success", message)
        toggle_to_login()      # switch back to login frame
    else:
        messagebox.showerror("Signup Failed", message)
```

---

## `open_customer_dashboard()` and `open_admin_dashboard()`

These functions live in `main.py`. They create a new `Tk()` root (or `Toplevel`), instantiate the respective dashboard class, and call `mainloop()`.

```python
def open_customer_dashboard():
    from customer.dashboard import CustomerDashboard
    root = tk.Tk()
    app = CustomerDashboard(root)
    root.mainloop()

def open_admin_dashboard():
    from admin.dashboard import AdminDashboard
    root = tk.Tk()
    app = AdminDashboard(root)
    root.mainloop()
```

---

## Validation Rules Summary

| Field | Rule |
|-------|------|
| Full Name | 2–80 chars, letters + spaces only |
| Email | Must match `r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'` |
| Phone | Exactly 10 digits (`r'^\d{10}$'`) |
| Password | Min 6 chars, ≥1 uppercase letter, ≥1 digit |
| Confirm Password | Must equal Password |
| Role | Exactly `'customer'` or `'admin'` |
