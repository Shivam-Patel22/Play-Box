# 09 — Full Code Skeleton
## Importable structure for every file in the project

---

## `main.py`

```python
"""
main.py — TurfBook Pro Entry Point
"""
import tkinter as tk
from tkinter import ttk
import database
import session
import utils

# ── Style applied once globally ──────────────────────────────────
def apply_global_style(root: tk.Tk) -> None:
    """See 05_UI_THEME.md for full implementation."""
    style = ttk.Style(root)
    style.theme_use("clam")
    # ... (all style.configure calls from UI_THEME.md)

# ── Dashboard launchers ───────────────────────────────────────────
def open_customer_dashboard() -> None:
    from customer.dashboard import CustomerDashboard
    root = tk.Tk()
    apply_global_style(root)
    app = CustomerDashboard(root)
    root.mainloop()

def open_admin_dashboard() -> None:
    from admin.dashboard import AdminDashboard
    root = tk.Tk()
    apply_global_style(root)
    app = AdminDashboard(root)
    root.mainloop()

# ── Auth Window ───────────────────────────────────────────────────
class AuthWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("TurfBook Pro — Login")
        self.root.resizable(False, False)
        utils.center_window(self.root, 500, 600)
        self.root.configure(bg="#1a472a")
        self._build_ui()

    def _build_ui(self):
        self.login_frame  = self._build_login_frame()
        self.signup_frame = self._build_signup_frame()
        self.login_frame.pack(fill="both", expand=True)

    def _build_login_frame(self) -> tk.Frame:
        """See 02_AUTH_MODULE.md LoginFrame Layout."""
        frame = tk.Frame(self.root, bg="#1a472a")
        # ... logo, title, card, fields, buttons
        return frame

    def _build_signup_frame(self) -> tk.Frame:
        """See 02_AUTH_MODULE.md SignupFrame Layout."""
        frame = tk.Frame(self.root, bg="#1a472a")
        # ... signup fields, role radio, buttons
        return frame

    def toggle_to_signup(self):
        self.login_frame.pack_forget()
        self.signup_frame.pack(fill="both", expand=True)

    def toggle_to_login(self):
        self.signup_frame.pack_forget()
        self.login_frame.pack(fill="both", expand=True)

    def on_login_click(self):
        import auth
        from tkinter import messagebox
        success, msg = auth.do_login(self.email_var.get(), self.pw_var.get())
        if success:
            role = session.get_role()
            self.root.destroy()
            if role == "customer":
                open_customer_dashboard()
            else:
                open_admin_dashboard()
        else:
            messagebox.showerror("Login Failed", msg)

    def on_signup_click(self):
        import auth
        from tkinter import messagebox
        success, msg = auth.do_signup(
            self.name_var.get(), self.email_var.get(), self.phone_var.get(),
            self.pw_var.get(), self.cpw_var.get(), self.role_var.get()
        )
        if success:
            messagebox.showinfo("Success", msg)
            self.toggle_to_login()
        else:
            messagebox.showerror("Signup Failed", msg)

# ── Main ──────────────────────────────────────────────────────────
def main():
    database.initialize_database()
    database.seed_demo_data()
    root = tk.Tk()
    apply_global_style(root)
    AuthWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
```

---

## `database.py`

```python
"""
database.py — All SQLite operations for TurfBook Pro
See 01_DATABASE_SCHEMA.md for complete SQL and function signatures.
"""
import sqlite3
import os
import utils

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "turf_booking.db")

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def initialize_database() -> None:
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users ( ... );
            CREATE TABLE IF NOT EXISTS turfs ( ... );
            CREATE TABLE IF NOT EXISTS bookings ( ... );
            CREATE TABLE IF NOT EXISTS payments ( ... );
            CREATE INDEX IF NOT EXISTS idx_turfs_sport ON turfs(sport);
            -- ... all indexes
        """)

def seed_demo_data() -> None:
    with get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if count > 0:
            return
        # Insert admin, customer, 10 turfs
        # (See 01_DATABASE_SCHEMA.md Seed Demo Data section)
        ...

# All function implementations from 01_DATABASE_SCHEMA.md
# create_user, get_user_by_email, get_user_by_id
# create_turf, update_turf, soft_delete_turf, get_turfs_by_owner
# search_turfs, get_turf_by_id, decrement_slots, increment_slots
# create_booking, get_bookings_by_customer, get_bookings_by_owner
# update_booking_status, update_payment_status, cancel_booking
# get_booking_by_id, check_slot_conflict
# create_payment, get_payment_by_booking
# get_revenue_by_turf
```

---

## `auth.py`

```python
"""
auth.py — Authentication logic for TurfBook Pro
See 02_AUTH_MODULE.md for complete implementations.
"""
import re
import utils
import database
import session

def hash_password(plain: str) -> str: ...
def verify_password(plain: str, stored_hash: str) -> bool: ...
def validate_signup_fields(...) -> list[str]: ...
def validate_login_fields(email, password) -> list[str]: ...
def do_signup(...) -> tuple[bool, str]: ...
def do_login(email, password) -> tuple[bool, str]: ...
```

---

## `session.py`

```python
"""
session.py — Global user session state
See 02_AUTH_MODULE.md for complete implementation.
"""
_current_user: dict | None = None

def set_user(user_row) -> None: ...
def get_user() -> dict | None: ...
def get_user_id() -> int | None: ...
def get_role() -> str | None: ...
def clear() -> None: ...
```

---

## `customer/__init__.py`
```python
# Empty file — marks directory as Python package
```

## `customer/dashboard.py`

```python
"""
customer/dashboard.py — Customer main window
See 03_CUSTOMER_DASHBOARD.md for full spec.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import session
import utils

class CustomerDashboard:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("TurfBook Pro — Customer Dashboard")
        self.root.minsize(1100, 700)
        utils.center_window(self.root, 1100, 700)
        self._build_ui()

    def _build_ui(self):
        self._build_header()
        self._build_notebook()

    def _build_header(self):
        """Dark green header with logo and logout."""
        header = tk.Frame(self.root, bg="#1a472a", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        # Logo, title, welcome text, logout button

    def _build_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=0, pady=0)

        from customer.search import SearchTab
        from customer.my_bookings import MyBookingsTab

        self.search_tab   = SearchTab(self.notebook, self)
        self.bookings_tab = MyBookingsTab(self.notebook, self)

        self.notebook.add(self.search_tab.frame,   text="  🔍 Browse Turfs  ")
        self.notebook.add(self.bookings_tab.frame, text="  📋 My Bookings  ")

    def refresh_bookings(self):
        """Called after payment completes to refresh My Bookings tab."""
        self.bookings_tab.load_bookings()

    def on_logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            session.clear()
            self.root.destroy()
            import subprocess, sys
            subprocess.Popen([sys.executable, "main.py"])
```

---

## `customer/search.py`

```python
"""
customer/search.py — Browse & Search Turfs tab
See 03_CUSTOMER_DASHBOARD.md SearchTab section.
"""
import tkinter as tk
from tkinter import ttk
import database
import utils

class SearchTab:
    def __init__(self, parent: ttk.Notebook, dashboard):
        self.dashboard = dashboard
        self.frame = tk.Frame(parent, bg="#f5f5f5")
        self._build_ui()
        self.load_all_turfs()

    def _build_ui(self):
        self._build_filter_bar()
        self._build_results_area()

    def _build_filter_bar(self): ...
    def _build_results_area(self): ...

    def load_all_turfs(self):
        results = database.search_turfs()
        self.render_turf_cards(results)

    def on_search(self): ...
    def on_reset(self): ...
    def render_turf_cards(self, results: list): ...
    def make_turf_card(self, parent, turf) -> tk.Frame: ...
    def show_turf_details(self, turf): ...
    def open_booking(self, turf): ...
```

---

## `customer/booking.py`

```python
"""
customer/booking.py — Booking form dialog
See 03_CUSTOMER_DASHBOARD.md BookingDialog section.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
import datetime
import database
import session
import utils

class BookingDialog(tk.Toplevel):
    def __init__(self, parent, turf: dict):
        super().__init__(parent)
        self.turf   = turf
        self.parent = parent
        self.title(f"Book Turf — {turf['name']}")
        self.resizable(False, False)
        utils.center_window(self, 480, 520)
        self.grab_set()
        self._build_ui()

    def _build_ui(self): ...
    def _build_header(self): ...
    def _build_calendar(self): ...
    def _build_time_selectors(self): ...
    def _build_price_display(self): ...
    def _build_buttons(self): ...

    def update_price_display(self, event=None): ...
    def on_confirm(self): ...
```

---

## `customer/my_bookings.py`

```python
"""
customer/my_bookings.py — My Bookings tab
See 03_CUSTOMER_DASHBOARD.md MyBookingsTab section.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import database
import session
import utils

class MyBookingsTab:
    def __init__(self, parent: ttk.Notebook, dashboard):
        self.dashboard = dashboard
        self.frame = tk.Frame(parent, bg="#f5f5f5")
        self._build_ui()
        self.load_bookings()

    def _build_ui(self): ...
    def _build_toolbar(self): ...
    def _build_treeview(self): ...

    def load_bookings(self): ...
    def on_cancel(self): ...
    def on_selection_change(self, event): ...
```

---

## `customer/payment.py`

```python
"""
customer/payment.py — Payment dialog and receipt
See 06_PAYMENT_MODULE.md for complete spec.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import database
import session
import utils

class PaymentDialog(tk.Toplevel):
    def __init__(self, parent, booking_id: int, turf: dict, total_price: float):
        super().__init__(parent)
        self.booking_id  = booking_id
        self.turf        = turf
        self.total_price = total_price
        self.parent      = parent
        self.title("Complete Payment — TurfBook Pro")
        self.resizable(False, False)
        utils.center_window(self, 500, 580)
        self.grab_set()
        self._build_ui()

    def _build_ui(self): ...
    def _build_order_summary(self): ...
    def _build_method_selector(self): ...
    def _build_upi_panel(self): ...
    def _build_card_panel(self, card_type: str): ...
    def _build_netbanking_panel(self): ...
    def _build_pay_button(self): ...

    def select_method(self, method: str): ...
    def show_method_panel(self, method: str): ...
    def validate_payment_fields(self, method: str) -> list[str]: ...
    def on_pay_click(self): ...
    def show_processing_popup(self) -> tk.Toplevel: ...
    def show_receipt(self, txn_id: str, method: str, amount: float): ...
```

---

## `admin/__init__.py`
```python
# Empty — marks directory as Python package
```

## `admin/dashboard.py`

```python
"""
admin/dashboard.py — Admin main window
See 04_ADMIN_DASHBOARD.md for full spec.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import session
import utils

class AdminDashboard:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("TurfBook Pro — Admin Panel")
        self.root.minsize(1200, 720)
        utils.center_window(self.root, 1200, 720)
        self._build_ui()

    def _build_ui(self):
        self._build_header()
        self._build_notebook()

    def _build_header(self): ...

    def _build_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        from admin.add_turf import AddTurfTab
        from admin.my_turfs import MyTurfsTab
        from admin.manage_bookings import ManageBookingsTab
        from admin.revenue import RevenueTab

        self.add_turf_tab       = AddTurfTab(self.notebook, self)
        self.my_turfs_tab       = MyTurfsTab(self.notebook, self)
        self.manage_bookings_tab= ManageBookingsTab(self.notebook, self)
        self.revenue_tab        = RevenueTab(self.notebook, self)

        self.notebook.add(self.add_turf_tab.frame,        text="  ➕ Add Turf  ")
        self.notebook.add(self.my_turfs_tab.frame,        text="  🏟️ My Turfs  ")
        self.notebook.add(self.manage_bookings_tab.frame, text="  📋 Bookings  ")
        self.notebook.add(self.revenue_tab.frame,         text="  📊 Revenue   ")

    def refresh_my_turfs(self):
        self.my_turfs_tab.load_turfs()

    def refresh_bookings(self):
        self.manage_bookings_tab.load_bookings()

    def on_logout(self): ...
```

---

## `admin/add_turf.py`

```python
"""
admin/add_turf.py — Add/Edit Turf form tab
See 04_ADMIN_DASHBOARD.md AddTurfTab section.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import database
import session
import utils

class AddTurfTab:
    def __init__(self, parent: ttk.Notebook, dashboard):
        self.dashboard       = dashboard
        self.editing_turf_id = None
        self.frame = tk.Frame(parent, bg="#f5f5f5")
        self._build_ui()

    def _build_ui(self): ...
    def _build_form(self): ...

    def browse_image(self): ...
    def show_preview(self, path: str): ...
    def clear_form(self): ...
    def load_turf_for_edit(self, turf): ...
    def validate_turf_fields(self, **fields) -> list[str]: ...
    def on_save(self): ...
```

---

## `admin/my_turfs.py`

```python
"""
admin/my_turfs.py — My Turfs management tab
See 04_ADMIN_DASHBOARD.md MyTurfsTab section.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import database
import session
import utils

class MyTurfsTab:
    def __init__(self, parent: ttk.Notebook, dashboard):
        self.dashboard = dashboard
        self.frame = tk.Frame(parent, bg="#f5f5f5")
        self._build_ui()
        self.load_turfs()

    def _build_ui(self): ...
    def _build_toolbar(self): ...
    def _build_treeview(self): ...

    def load_turfs(self): ...
    def on_edit(self): ...
    def on_delete(self): ...
```

---

## `admin/manage_bookings.py`

```python
"""
admin/manage_bookings.py — Booking management tab
See 04_ADMIN_DASHBOARD.md ManageBookingsTab section.
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import database
import session
import utils

class ManageBookingsTab:
    def __init__(self, parent: ttk.Notebook, dashboard):
        self.dashboard = dashboard
        self.frame = tk.Frame(parent, bg="#f5f5f5")
        self._build_ui()
        self.load_bookings()

    def _build_ui(self): ...
    def _build_filter_bar(self): ...
    def _build_treeview(self): ...
    def _build_action_buttons(self): ...

    def load_bookings(self): ...
    def on_accept(self): ...
    def on_reject(self): ...
```

---

## `admin/revenue.py`

```python
"""
admin/revenue.py — Revenue dashboard with Matplotlib chart
See 04_ADMIN_DASHBOARD.md RevenueTab section.
"""
import tkinter as tk
from tkinter import ttk
import database
import session
import utils

class RevenueTab:
    def __init__(self, parent: ttk.Notebook, dashboard):
        self.dashboard = dashboard
        self.frame = tk.Frame(parent, bg="#f5f5f5")
        self._build_ui()
        self.load_data()

    def _build_ui(self): ...
    def _build_summary_cards(self): ...
    def _build_chart_area(self): ...

    def load_data(self): ...
    def render_summary(self): ...
    def render_chart(self): ...
```
