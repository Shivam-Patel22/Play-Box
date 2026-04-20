# 03 — Customer Dashboard Specification
## Files: `customer/dashboard.py` · `customer/search.py` · `customer/booking.py` · `customer/my_bookings.py`

---

## `customer/dashboard.py` — Main Container

### Window Properties
```
Title       : TurfBook Pro — Customer Dashboard
Size        : 1100 × 700  (minimum, resizable)
Position    : Centered on screen
Background  : #f5f5f5
```

### Layout

```
┌─────────────────────────────────────────────────────────────┐
│  HEADER BAR (bg=#1a472a, height=60)                         │
│  [🏟️ TurfBook Pro]  (logo+title left)    [👤 John Doe  🚪 Logout] (right) │
├─────────────────────────────────────────────────────────────┤
│  NOTEBOOK (ttk.Notebook, fills remaining space)             │
│  ┌──────────────┬──────────────────────┐                   │
│  │ 🔍 Browse    │ 📋 My Bookings       │                   │
│  └──────────────┴──────────────────────┘                   │
│                                                             │
│  [Tab Content renders here]                                 │
└─────────────────────────────────────────────────────────────┘
```

### Header Bar Widget Details
| Element | Details |
|---------|---------|
| Logo + Title | `Label` "🏟️ TurfBook Pro", fg=#f0a500, font=("Arial",16,"bold") |
| Welcome text | `Label` "Welcome, {full_name}", fg=#c8e6c9, font=("Arial",11) |
| Logout button | `Button` text="🚪 Logout", bg=#c0392b, fg=white, cursor=hand2 |

### Logout Handler
```python
def on_logout():
    if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
        session.clear()
        self.root.destroy()
        # Re-launch main.py auth window
        import subprocess, sys
        subprocess.Popen([sys.executable, "main.py"])
```

### Notebook Tabs
```python
notebook = ttk.Notebook(main_frame)
search_tab    = SearchTab(notebook)
bookings_tab  = MyBookingsTab(notebook)
notebook.add(search_tab.frame,    text="  🔍 Browse Turfs  ")
notebook.add(bookings_tab.frame,  text="  📋 My Bookings  ")
```

---

## `customer/search.py` — Browse & Search Turfs Tab

### Layout

```
┌──────────────────────────────────────────────────────────────┐
│  FILTER BAR (bg=#ffffff, pady=15)                            │
│  Sport: [Dropdown ▼]  Area: [________________]  [🔍 Search] [🔄 Reset] │
├──────────────────────────────────────────────────────────────┤
│  RESULTS LABEL: "Showing 10 turfs"                           │
├──────────────────────────────────────────────────────────────┤
│  SCROLLABLE CARD GRID (Canvas + Scrollbar)                   │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │  ⚽ FOOTBALL      │  │  🏏 CRICKET       │                │
│  │  Goal Zone Arena  │  │  Sunrise Ground   │                │
│  │  📍 Satellite     │  │  📍 Bopal         │                │
│  │  ₹700/hr  ●2 slots│  │  ₹800/hr  ●3 slots│               │
│  │  [View Details]   │  │  [View Details]   │                │
│  │  [Book Now  →]    │  │  [Book Now  →]    │                │
│  └──────────────────┘  └──────────────────┘                │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Filter Bar Widgets

| Widget | Type | Details |
|--------|------|---------|
| Sport label | `Label` | "Sport:" |
| Sport dropdown | `ttk.Combobox` | values=["All","Cricket","Football","Pickleball","Pool","Snooker"], state="readonly", width=15 |
| Area label | `Label` | "Area / Location:" |
| Area entry | `ttk.Entry` | width=25, textvariable=area_var |
| Search button | `Button` | bg=#1a472a, fg=white, text="🔍 Search", calls on_search() |
| Reset button | `Button` | bg=#7f8c8d, fg=white, text="🔄 Reset", clears filters and reloads all |

### `on_search()`
```python
def on_search():
    sport = sport_var.get()
    area  = area_var.get().strip()
    sport_filter = "" if sport == "All" else sport
    results = database.search_turfs(sport=sport_filter, area=area)
    render_turf_cards(results)
    result_label.config(text=f"Showing {len(results)} turf(s)")
```

### Scrollable Cards Implementation
```python
# Use Canvas + Frame + Scrollbar pattern
canvas    = tk.Canvas(parent, bg="#f5f5f5", highlightthickness=0)
scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
scroll_frame = tk.Frame(canvas, bg="#f5f5f5")
canvas.create_window((0,0), window=scroll_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)
scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
# Bind mousewheel
canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
```

### Turf Card — `render_turf_cards(results)`
```python
# Clear scroll_frame children first
for widget in scroll_frame.winfo_children():
    widget.destroy()

COLS = 3   # cards per row
for i, turf in enumerate(results):
    row, col = divmod(i, COLS)
    card = make_turf_card(scroll_frame, turf)
    card.grid(row=row, column=col, padx=12, pady=12, sticky="nsew")
```

### `make_turf_card(parent, turf)` → `Frame`

```
Card Frame:  bg=#ffffff, width=300, relief=flat, borderwidth=1
             Hover effect: bd=2, highlightbackground=#1a472a

┌─────────────────────────────────┐
│  [Sport Icon 48×48 or emoji]    │ ← centered, pady=10
│  ⚽ FOOTBALL    (sport badge)   │ ← colored badge (see sport colors)
│  Goal Zone Arena                │ ← font=("Arial",14,"bold")
│  📍 Satellite, Ahmedabad        │ ← font=("Arial",10), fg=#666
│  ─────────────────────────────  │
│  ₹700 / hour                    │ ← fg=#1a472a, font=bold,14
│  🟢 2 slots available           │ ← green if >0, red "Fully Booked" if 0
│  ─────────────────────────────  │
│  [View Details]  [Book Now →]   │ ← two buttons side by side
└─────────────────────────────────┘
```

### Sport Badge Colors
| Sport | Background | Text |
|-------|-----------|------|
| Cricket | #2e7d32 | white |
| Football | #1565c0 | white |
| Pickleball | #e65100 | white |
| Pool | #4a148c | white |
| Snooker | #880e4f | white |

### Sport Emoji Map
```python
SPORT_EMOJI = {
    "Cricket":    "🏏",
    "Football":   "⚽",
    "Pickleball": "🏓",
    "Pool":       "🎱",
    "Snooker":    "🎯",
}
```

### View Details Button — `show_turf_details(turf)`
Opens a `Toplevel` popup (400×500) with:
- Full turf image (if image_path exists, else placeholder)
- All fields: name, sport, area, location, price/hr, available slots, description
- A "Book Now" button at the bottom

### Book Now Button — `open_booking(turf)`
Calls `BookingDialog(parent, turf)` from `customer/booking.py`.

---

## `customer/booking.py` — Booking Dialog

### `BookingDialog(parent, turf)` — Toplevel Popup

### Window Properties
```
Title    : Book Turf — {turf_name}
Size     : 480 × 520
Resizable: False
Modal    : Yes (grab_set)
```

### Layout

```
┌──────────────────────────────────────────┐
│  Book: Goal Zone Football Arena          │  ← title
│  ⚽ Football · 📍 Satellite · ₹700/hr   │  ← subtitle
├──────────────────────────────────────────┤
│                                          │
│  Select Date:                            │
│  [Calendar widget — tkcalendar]          │
│                                          │
│  Start Time:  [HH ▼] : [MM ▼]           │
│  End Time:    [HH ▼] : [MM ▼]           │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │  Duration: 2 hrs 0 mins          │   │
│  │  Total Price: ₹1,400.00          │   │
│  └──────────────────────────────────┘   │
│                                          │
│  [ ✕ Cancel ]        [ ✔ Confirm Book ] │
└──────────────────────────────────────────┘
```

### Calendar Widget
```python
from tkcalendar import Calendar
cal = Calendar(
    parent,
    selectmode="day",
    mindate=datetime.date.today(),          # cannot book in the past
    date_pattern="yyyy-mm-dd",
    background="#1a472a",
    foreground="white",
    headersbackground="#0d3320",
    normalbackground="#ffffff",
    weekendbackground="#f0f8f0",
)
```

### Time Dropdowns
```python
# Hours: ["06","07","08","09","10","11","12","13","14","15","16","17","18","19","20","21","22"]
# Minutes: ["00","15","30","45"]
# Both are ttk.Combobox, state="readonly", width=5
# Start time default: 08:00
# End time default: 09:00
```

### Price Calculation — `update_price_display()`
```python
def update_price_display():
    start = int(start_h.get()) * 60 + int(start_m.get())
    end   = int(end_h.get())   * 60 + int(end_m.get())
    if end <= start:
        duration_label.config(text="⚠ End time must be after start time", fg="red")
        total_label.config(text="")
        return
    duration_mins = end - start
    duration_hrs  = duration_mins / 60
    price         = duration_hrs * turf["price_per_hour"]
    duration_label.config(
        text=f"Duration: {duration_mins // 60} hr {duration_mins % 60} min", fg="#333"
    )
    total_label.config(text=f"Total Price: ₹{price:,.2f}", fg="#1a472a")
```

Bind `update_price_display` to `<<ComboboxSelected>>` on all four dropdowns.

### Confirm Book Button — `on_confirm()`
```python
def on_confirm():
    date       = cal.get_date()              # "YYYY-MM-DD"
    start_time = f"{start_h.get()}:{start_m.get()}"
    end_time   = f"{end_h.get()}:{end_m.get()}"

    # Validation
    if end_time <= start_time:
        messagebox.showerror("Invalid Time", "End time must be after start time.")
        return
    if turf["available_slots"] == 0:
        messagebox.showerror("Fully Booked", "No slots available for this turf.")
        return

    # Conflict check
    if database.check_slot_conflict(turf["id"], date, start_time, end_time):
        messagebox.showerror(
            "Time Conflict",
            "A booking already exists for this time slot. Please choose a different time."
        )
        return

    # Calculate price
    start_mins = int(start_h.get())*60 + int(start_m.get())
    end_mins   = int(end_h.get())*60   + int(end_m.get())
    price      = ((end_mins - start_mins) / 60) * turf["price_per_hour"]

    # Create booking
    booking_id = database.create_booking(
        session.get_user_id(), turf["id"], date, start_time, end_time, price
    )

    self.destroy()   # close booking dialog

    # Open payment dialog
    from customer.payment import PaymentDialog
    PaymentDialog(parent, booking_id, turf, price)
```

---

## `customer/my_bookings.py` — My Bookings Tab

### Layout

```
┌──────────────────────────────────────────────────────────────────────┐
│  My Bookings                    [🔄 Refresh]                        │
├──────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ Turf Name   │ Sport │ Date │ Time │ Amount │ Status │ Payment  │ │
│  ├─────────────┼───────┼──────┼──────┼────────┼────────┼──────────┤ │
│  │ Goal Zone   │  ⚽   │10/04 │08-10 │ ₹1400  │Pending │ Unpaid   │ │
│  │ Sunrise Grd │  🏏   │11/04 │09-11 │ ₹1600  │Confirm │ Paid     │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  [✕ Cancel Booking]  (enabled only when selected row is Pending)     │
└──────────────────────────────────────────────────────────────────────┘
```

### Treeview Setup
```python
columns = ("turf","sport","date","time","amount","status","payment")
tree = ttk.Treeview(frame, columns=columns, show="headings", height=18)
tree.heading("turf",    text="Turf Name")
tree.heading("sport",   text="Sport")
tree.heading("date",    text="Date")
tree.heading("time",    text="Time Slot")
tree.heading("amount",  text="Amount")
tree.heading("status",  text="Status")
tree.heading("payment", text="Payment")

tree.column("turf",    width=200)
tree.column("sport",   width=100)
tree.column("date",    width=90)
tree.column("time",    width=110)
tree.column("amount",  width=90)
tree.column("status",  width=100)
tree.column("payment", width=90)
```

### Row Tag Colors
```python
tree.tag_configure("Pending",   background="#fff9c4")  # light yellow
tree.tag_configure("Confirmed", background="#c8e6c9")  # light green
tree.tag_configure("Rejected",  background="#ffcdd2")  # light red
tree.tag_configure("Cancelled", background="#f5f5f5")  # grey
```

### `load_bookings()`
```python
def load_bookings():
    for row in tree.get_children():
        tree.delete(row)
    bookings = database.get_bookings_by_customer(session.get_user_id())
    for b in bookings:
        time_str = f"{b['start_time']} – {b['end_time']}"
        tree.insert("", "end", iid=b["id"], values=(
            b["turf_name"], b["sport"], b["booking_date"],
            time_str, f"₹{b['total_price']:,.0f}",
            b["status"], b["payment_status"]
        ), tags=(b["status"],))
```

### Cancel Booking Button — `on_cancel()`
```python
def on_cancel():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Select Booking", "Please select a booking to cancel.")
        return
    booking_id = int(selected[0])
    booking = database.get_booking_by_id(booking_id)
    if booking["status"] != "Pending":
        messagebox.showerror("Cannot Cancel",
            "Only Pending bookings can be cancelled.")
        return
    if messagebox.askyesno("Confirm Cancel",
            "Are you sure you want to cancel this booking?"):
        database.cancel_booking(booking_id)
        messagebox.showinfo("Cancelled", "Booking cancelled successfully.")
        load_bookings()
```

Note: Cancel is enabled only for `status = "Pending"`. Confirmed/Rejected/Cancelled rows show the button disabled or grayed.
