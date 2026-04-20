# 01 — Database Schema Specification
## File: `database.py`

---

## Database File
```
turf_booking.db   (created automatically in project root on first run)
```

---

## Table 1: `users`

```sql
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name     TEXT    NOT NULL,
    email         TEXT    NOT NULL UNIQUE,
    phone         TEXT    NOT NULL,
    password_hash TEXT    NOT NULL,
    role          TEXT    NOT NULL CHECK(role IN ('customer', 'admin')),
    created_at    TEXT    DEFAULT (datetime('now'))
);
```

### Notes
- `email` must be unique across all users (both roles)
- `role` is strictly `'customer'` or `'admin'` — enforced by CHECK constraint
- `password_hash` stores SHA-256 hex digest only
- `created_at` auto-set on insert via SQLite default

---

## Table 2: `turfs`

```sql
CREATE TABLE IF NOT EXISTS turfs (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id         INTEGER NOT NULL,
    name             TEXT    NOT NULL,
    sport            TEXT    NOT NULL CHECK(sport IN (
                         'Cricket','Football','Pickleball','Pool','Snooker'
                     )),
    area             TEXT    NOT NULL,
    location         TEXT    NOT NULL,
    price_per_hour   REAL    NOT NULL CHECK(price_per_hour > 0),
    available_slots  INTEGER NOT NULL DEFAULT 1 CHECK(available_slots >= 0),
    description      TEXT,
    image_path       TEXT,
    is_active        INTEGER NOT NULL DEFAULT 1,
    created_at       TEXT    DEFAULT (datetime('now')),
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### Notes
- `owner_id` references `users.id` — must be an admin user
- `sport` is one of the five allowed values only
- `price_per_hour` is stored as REAL (e.g., 500.00 = ₹500/hr)
- `available_slots` counts concurrent bookings allowed at this turf
- `is_active` soft-delete flag (0 = deleted, 1 = live) — never hard-delete turfs with bookings
- `image_path` stores absolute path to image file (can be NULL)

---

## Table 3: `bookings`

```sql
CREATE TABLE IF NOT EXISTS bookings (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id    INTEGER NOT NULL,
    turf_id        INTEGER NOT NULL,
    booking_date   TEXT    NOT NULL,           -- Format: YYYY-MM-DD
    start_time     TEXT    NOT NULL,           -- Format: HH:MM  (24-hour)
    end_time       TEXT    NOT NULL,           -- Format: HH:MM  (24-hour)
    total_price    REAL    NOT NULL,
    status         TEXT    NOT NULL DEFAULT 'Pending'
                           CHECK(status IN ('Pending','Confirmed','Rejected','Cancelled')),
    payment_status TEXT    NOT NULL DEFAULT 'Unpaid'
                           CHECK(payment_status IN ('Unpaid','Paid')),
    created_at     TEXT    DEFAULT (datetime('now')),
    FOREIGN KEY (customer_id) REFERENCES users(id),
    FOREIGN KEY (turf_id)     REFERENCES turfs(id)
);
```

### Status Flow

```
[Customer Books]  →  status: "Pending",  payment_status: "Unpaid"
       ↓
[Customer Pays]   →  payment_status: "Paid"   (status stays Pending until admin acts)
       ↓
[Admin Accepts]   →  status: "Confirmed"   → available_slots -= 1
[Admin Rejects]   →  status: "Rejected"   → available_slots unchanged
[Customer Cancel] →  status: "Cancelled"  → available_slots += 1 if was Confirmed
```

### total_price Calculation
```
total_price = price_per_hour × duration_in_hours
duration    = (end_time_minutes - start_time_minutes) / 60
```

---

## Table 4: `payments`

```sql
CREATE TABLE IF NOT EXISTS payments (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id     INTEGER NOT NULL UNIQUE,    -- one payment per booking
    customer_id    INTEGER NOT NULL,
    amount         REAL    NOT NULL,
    method         TEXT    NOT NULL CHECK(method IN ('UPI','Credit Card','Debit Card','Net Banking')),
    transaction_id TEXT    NOT NULL UNIQUE,
    timestamp      TEXT    DEFAULT (datetime('now')),
    FOREIGN KEY (booking_id)  REFERENCES bookings(id),
    FOREIGN KEY (customer_id) REFERENCES users(id)
);
```

### Notes
- `transaction_id` is auto-generated: `TXN` + 12 random uppercase alphanumeric chars
- `UNIQUE` on `booking_id` prevents double-payment
- `amount` should equal `bookings.total_price`

---

## Indexes

```sql
CREATE INDEX IF NOT EXISTS idx_turfs_sport    ON turfs(sport);
CREATE INDEX IF NOT EXISTS idx_turfs_area     ON turfs(area);
CREATE INDEX IF NOT EXISTS idx_turfs_owner    ON turfs(owner_id);
CREATE INDEX IF NOT EXISTS idx_bookings_cust  ON bookings(customer_id);
CREATE INDEX IF NOT EXISTS idx_bookings_turf  ON bookings(turf_id);
CREATE INDEX IF NOT EXISTS idx_bookings_date  ON bookings(booking_date);
```

---

## `database.py` — Full Function Signatures

```python
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "turf_booking.db")

def get_connection() -> sqlite3.Connection:
    """Return a connection with row_factory = sqlite3.Row."""

def initialize_database() -> None:
    """Create all tables and indexes if they do not exist. Called once on startup."""

def seed_demo_data() -> None:
    """
    Insert demo admin + 10 sample turfs if users table is empty.
    Demo Admin: email=admin@turfbook.com  password=Admin@123
    Demo Customer: email=user@turfbook.com  password=User@123
    """

# ── USER FUNCTIONS ──────────────────────────────────────────────
def create_user(full_name: str, email: str, phone: str,
                password_hash: str, role: str) -> int:
    """Insert new user. Returns new user id. Raises ValueError on duplicate email."""

def get_user_by_email(email: str) -> sqlite3.Row | None:
    """Return user row by email, or None."""

def get_user_by_id(user_id: int) -> sqlite3.Row | None:
    """Return user row by id, or None."""

# ── TURF FUNCTIONS ───────────────────────────────────────────────
def create_turf(owner_id: int, name: str, sport: str, area: str,
                location: str, price_per_hour: float,
                available_slots: int, description: str,
                image_path: str | None) -> int:
    """Insert turf. Returns new turf id."""

def update_turf(turf_id: int, name: str, sport: str, area: str,
                location: str, price_per_hour: float,
                available_slots: int, description: str,
                image_path: str | None) -> None:
    """Update turf fields by id."""

def soft_delete_turf(turf_id: int) -> None:
    """Set is_active=0 for the turf."""

def get_turfs_by_owner(owner_id: int) -> list[sqlite3.Row]:
    """Return all active turfs owned by admin."""

def search_turfs(sport: str = "", area: str = "") -> list[sqlite3.Row]:
    """
    Return active turfs filtered by sport and/or area (case-insensitive LIKE).
    If both empty, return all active turfs.
    """

def get_turf_by_id(turf_id: int) -> sqlite3.Row | None:
    """Return single turf row by id."""

def decrement_slots(turf_id: int) -> None:
    """Reduce available_slots by 1 (called on booking Confirm)."""

def increment_slots(turf_id: int) -> None:
    """Increase available_slots by 1 (called on booking Cancel if Confirmed)."""

# ── BOOKING FUNCTIONS ────────────────────────────────────────────
def create_booking(customer_id: int, turf_id: int, booking_date: str,
                   start_time: str, end_time: str,
                   total_price: float) -> int:
    """Insert booking with status=Pending, payment_status=Unpaid. Returns booking id."""

def get_bookings_by_customer(customer_id: int) -> list[sqlite3.Row]:
    """
    Return all bookings for a customer with joined turf name and sport.
    ORDER BY created_at DESC.
    """

def get_bookings_by_owner(owner_id: int) -> list[sqlite3.Row]:
    """
    Return all bookings for turfs owned by this admin.
    Joins: bookings → turfs → users (customer name).
    ORDER BY bookings.created_at DESC.
    """

def update_booking_status(booking_id: int, status: str) -> None:
    """Set bookings.status. Allowed: Confirmed / Rejected / Cancelled."""

def update_payment_status(booking_id: int) -> None:
    """Set payment_status='Paid' for booking_id."""

def cancel_booking(booking_id: int) -> None:
    """
    Set status='Cancelled'.
    If previous status was 'Confirmed', call increment_slots on its turf_id.
    """

def get_booking_by_id(booking_id: int) -> sqlite3.Row | None:
    """Return single booking row."""

def check_slot_conflict(turf_id: int, booking_date: str,
                        start_time: str, end_time: str) -> bool:
    """
    Return True if a Confirmed booking exists for this turf on this date
    that overlaps the requested time window.
    Overlap condition: existing.start < requested.end AND existing.end > requested.start
    """

# ── PAYMENT FUNCTIONS ────────────────────────────────────────────
def create_payment(booking_id: int, customer_id: int, amount: float,
                   method: str, transaction_id: str) -> int:
    """Insert payment record. Returns payment id."""

def get_payment_by_booking(booking_id: int) -> sqlite3.Row | None:
    """Return payment row for a booking, or None if not yet paid."""

# ── REVENUE FUNCTIONS ────────────────────────────────────────────
def get_revenue_by_turf(owner_id: int) -> list[tuple[str, float]]:
    """
    Return list of (turf_name, total_revenue) for all turfs owned by admin
    where payment_status='Paid'.
    """
```

---

## Seed Demo Data (for `seed_demo_data`)

### Admin Account
```
full_name : Demo Admin
email     : admin@turfbook.com
password  : Admin@123   (stored as sha256 hash)
phone     : 9876543210
role      : admin
```

### Customer Account
```
full_name : Demo Customer
email     : user@turfbook.com
password  : User@123   (stored as sha256 hash)
phone     : 9123456789
role      : customer
```

### Sample Turfs (10 records, all owner_id = admin user)
```
1.  name=Sunrise Cricket Ground    sport=Cricket     area=Bopal        location=Bopal, Ahmedabad     price=800  slots=3
2.  name=Goal Zone Football Arena  sport=Football    area=Satellite    location=Satellite, Ahmedabad  price=700  slots=2
3.  name=Smash Pickleball Court    sport=Pickleball  area=Navrangpura  location=Navrangpura, Ahmedabad price=400 slots=4
4.  name=Cue Masters Pool Hall     sport=Pool        area=CG Road      location=CG Road, Ahmedabad    price=300  slots=6
5.  name=Snooker Palace            sport=Snooker     area=Maninagar    location=Maninagar, Ahmedabad  price=350  slots=5
6.  name=City Cricket Club         sport=Cricket     area=Vastrapur    location=Vastrapur, Ahmedabad  price=1000 slots=2
7.  name=Green Turf Football       sport=Football    area=Bopal        location=Bopal, Ahmedabad      price=600  slots=3
8.  name=ProPick Pickleball        sport=Pickleball  area=Satellite    location=Satellite, Ahmedabad  price=450  slots=3
9.  name=Break Point Snooker       sport=Snooker     area=Navrangpura  location=Navrangpura, Ahmedabad price=400 slots=4
10. name=Pool Sharks Arena         sport=Pool        area=Vastrapur    location=Vastrapur, Ahmedabad  price=280  slots=8
```
