# 🏟️ TurfBook Pro — Complete Turf Booking Desktop Application
## Master Specification Document

> **Tech Stack:** Python · Tkinter (ttk) · SQLite3 · tkcalendar · Matplotlib · Pillow  
> **Grade:** Production-Ready  
> **Platform:** Windows / macOS / Linux Desktop  
> **Version:** 1.0.0

---

## 📁 Full Project Structure

```
turf_booking/
│
├── main.py                        # Entry point — launches app, initializes DB
├── database.py                    # All SQLite operations, schema, seed data
├── auth.py                        # Login / Signup logic & session management
├── session.py                     # Global session state (logged-in user)
├── utils.py                       # Shared helpers: center_window, hash, format_time
│
├── customer/
│   ├── __init__.py
│   ├── dashboard.py               # Customer main window (Notebook container)
│   ├── search.py                  # Search & Browse Turfs tab
│   ├── booking.py                 # Booking form popup & logic
│   ├── my_bookings.py             # My Bookings tab
│   └── payment.py                 # Payment screen & receipt
│
├── admin/
│   ├── __init__.py
│   ├── dashboard.py               # Admin main window (Notebook container)
│   ├── add_turf.py                # Add / Edit Turf form
│   ├── my_turfs.py                # View & manage own turfs
│   ├── manage_bookings.py         # Accept / Reject bookings
│   └── revenue.py                 # Revenue chart (Matplotlib)
│
├── assets/
│   ├── icons/                     # .png icons for buttons & sports
│   └── logo.png                   # App logo
│
├── requirements.txt               # pip dependencies
└── setup.py                       # Optional: packaging script
```

---

## 📄 Specification Files in This Package

| File | Contents |
|------|----------|
| `01_DATABASE_SCHEMA.md` | Full SQLite schema, all tables, indexes, constraints |
| `02_AUTH_MODULE.md` | Login, Signup, password hashing, session management |
| `03_CUSTOMER_DASHBOARD.md` | All customer screens: search, booking, payments, history |
| `04_ADMIN_DASHBOARD.md` | All admin screens: add turf, manage bookings, revenue |
| `05_UI_THEME.md` | Complete colour palette, fonts, styles, widget rules |
| `06_PAYMENT_MODULE.md` | Payment simulation, receipt generation, transaction IDs |
| `07_UTILS_AND_HELPERS.md` | All shared utility functions with full signatures |
| `08_REQUIREMENTS.md` | pip packages, versions, installation instructions |
| `09_FULL_CODE_SKELETON.md` | Importable code skeleton for every file |
| `10_ERROR_HANDLING.md` | All error states, validation rules, messagebox patterns |

---

## 🏅 Sports Supported

| Sport | Icon Tag | Min Duration |
|-------|----------|-------------|
| Cricket | 🏏 | 1 hour |
| Football | ⚽ | 1 hour |
| Pickleball | 🏓 | 30 min |
| Pool (Billiards) | 🎱 | 30 min |
| Snooker | 🎯 | 30 min |

---

## 🎯 Core Features Summary

### Customer
- Register & Login with hashed password
- Search turfs by **Sport** and/or **Area / Location**
- View turf details (price, slots, description)
- Book turf with **date + time slot picker**
- Pay via simulated UPI / Card / Net Banking
- View all personal bookings with status
- Cancel pending bookings

### Admin (Turf Owner)
- Register & Login as Admin
- Add new turf with full details + optional image
- Edit or Delete owned turfs
- View all incoming bookings for owned turfs
- **Accept** (confirms booking, reduces slots) or **Reject** bookings
- Revenue dashboard with Matplotlib bar chart

---

## 🔐 Security Rules
- Passwords hashed with SHA-256 via `hashlib`
- No plain-text passwords ever stored
- Admin can only see/manage **their own** turfs and bookings
- Customers can only cancel **their own** bookings with status **"Pending"**
- All DB inputs use parameterised queries (no SQL injection)
