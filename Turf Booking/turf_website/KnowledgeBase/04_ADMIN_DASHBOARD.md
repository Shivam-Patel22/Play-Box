# 04 — Admin Dashboard Specification
## Files: `admin/dashboard.py` · `admin/add_turf.py` · `admin/my_turfs.py` · `admin/manage_bookings.py` · `admin/revenue.py`

---

## `admin/dashboard.py` — Main Container

### Window Properties
```
Title       : TurfBook Pro — Admin Panel
Size        : 1200 × 720  (minimum, resizable)
Position    : Centered on screen
Background  : #f5f5f5
```

### Layout

```
┌──────────────────────────────────────────────────────────────────────┐
│  HEADER (bg=#0d3320, height=60)                                     │
│  [🏟️ TurfBook Pro — Admin Panel]  (left)    [👤 Admin Name  🚪 Logout] (right) │
├──────────────────────────────────────────────────────────────────────┤
│  NOTEBOOK (ttk.Notebook fills rest)                                  │
│  ┌──────────────┬──────────────┬───────────────┬──────────────────┐ │
│  │ ➕ Add Turf  │ 🏟️ My Turfs  │ 📋 Bookings   │ 📊 Revenue       │ │
│  └──────────────┴──────────────┴───────────────┴──────────────────┘ │
│  [Tab Content]                                                        │
└──────────────────────────────────────────────────────────────────────┘
```

### Tabs
```python
notebook.add(add_turf_tab.frame,      text="  ➕ Add Turf  ")
notebook.add(my_turfs_tab.frame,      text="  🏟️ My Turfs  ")
notebook.add(manage_bookings_tab.frame,text="  📋 Bookings  ")
notebook.add(revenue_tab.frame,       text="  📊 Revenue   ")
```

---

## `admin/add_turf.py` — Add / Edit Turf Tab

### Layout

```
┌────────────────────────────────────────────────────────────┐
│  Add New Turf                                               │
│  Fill in the details below to list your turf               │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌────────────────────────┐  ┌───────────────────────┐    │
│  │  LEFT COLUMN           │  │  RIGHT COLUMN          │    │
│  │                        │  │                        │    │
│  │  Turf Name *           │  │  Sport *               │    │
│  │  [________________]    │  │  [Dropdown ▼]          │    │
│  │                        │  │                        │    │
│  │  Area *                │  │  Location / Address *  │    │
│  │  [________________]    │  │  [________________]    │    │
│  │                        │  │                        │    │
│  │  Price per Hour (₹) *  │  │  Available Slots *     │    │
│  │  [________________]    │  │  [________________]    │    │
│  │                        │  │                        │    │
│  └────────────────────────┘  └───────────────────────┘    │
│                                                             │
│  Description (optional):                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  [Multi-line Text widget, height=5]                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  Turf Image (optional):                                     │
│  [Browse Image...]    /path/to/image.jpg    [Preview]       │
│                                                             │
│  [🔄 Clear Form]               [💾 Save Turf]               │
└────────────────────────────────────────────────────────────┘
```

### Field Widgets

| Field | Type | Validation |
|-------|------|-----------|
| Turf Name | `ttk.Entry` | Required, 3–100 chars |
| Sport | `ttk.Combobox` | Required, one of 5 sports |
| Area | `ttk.Entry` | Required, 2–50 chars |
| Location | `ttk.Entry` | Required, 5–200 chars |
| Price/hr | `ttk.Entry` | Required, positive number |
| Slots | `ttk.Entry` | Required, integer 1–50 |
| Description | `tk.Text` | Optional, max 500 chars |
| Image | `ttk.Entry` + Browse button | Optional, valid file path |

### Browse Image Button
```python
def browse_image():
    path = filedialog.askopenfilename(
        title="Select Turf Image",
        filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp")]
    )
    if path:
        image_path_var.set(path)
        show_preview(path)

def show_preview(path):
    from PIL import Image, ImageTk
    img = Image.open(path).resize((120, 80), Image.LANCZOS)
    photo = ImageTk.PhotoImage(img)
    preview_label.config(image=photo)
    preview_label.image = photo   # keep reference
```

### Save Turf — `on_save()`
```python
def on_save():
    errors = validate_turf_fields(...)
    if errors:
        messagebox.showerror("Validation Error", "\n".join(errors))
        return
    if editing_turf_id:
        database.update_turf(editing_turf_id, ...)
        messagebox.showinfo("Updated", "Turf updated successfully!")
    else:
        database.create_turf(session.get_user_id(), ...)
        messagebox.showinfo("Saved", "Turf listed successfully!")
    clear_form()
    # Refresh My Turfs tab
    dashboard.refresh_my_turfs()
```

### Validate Turf Fields
```python
def validate_turf_fields(name, sport, area, location, price, slots) -> list[str]:
    errors = []
    if not name or len(name.strip()) < 3:
        errors.append("Turf Name must be at least 3 characters.")
    if sport not in ["Cricket","Football","Pickleball","Pool","Snooker"]:
        errors.append("Please select a valid sport.")
    if not area.strip():
        errors.append("Area is required.")
    if not location.strip():
        errors.append("Location is required.")
    try:
        p = float(price)
        if p <= 0: raise ValueError
    except ValueError:
        errors.append("Price must be a positive number.")
    try:
        s = int(slots)
        if s < 1 or s > 50: raise ValueError
    except ValueError:
        errors.append("Slots must be a whole number between 1 and 50.")
    return errors
```

### Edit Mode
The `AddTurfTab` supports both **Add** and **Edit** modes.

When the admin clicks **Edit** in `MyTurfsTab`, call:
```python
add_turf_tab.load_turf_for_edit(turf_row)
notebook.select(add_turf_tab.frame)
```

`load_turf_for_edit(turf)` populates all form fields with existing values and sets `editing_turf_id`.
The Save button label changes to "💾 Update Turf".

---

## `admin/my_turfs.py` — My Turfs Tab

### Layout

```
┌───────────────────────────────────────────────────────────────────┐
│  My Turfs  (2 turfs listed)           [➕ Add New Turf]  [🔄 Refresh] │
├───────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ Name        │ Sport    │ Area     │ Price/hr │ Slots │ Status│  │
│  ├─────────────┼──────────┼──────────┼──────────┼───────┼───────┤  │
│  │ Goal Zone   │ Football │ Satellite│ ₹700     │   2   │ Active│  │
│  │ Snooker Pal │ Snooker  │ Maninagar│ ₹350     │   5   │ Active│  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  [✏️ Edit Selected]           [🗑 Delete Selected]                 │
└───────────────────────────────────────────────────────────────────┘
```

### Treeview Columns
```python
columns = ("name","sport","area","price","slots","status")
headings = {
    "name" : ("Turf Name", 220),
    "sport": ("Sport",     110),
    "area" : ("Area",      120),
    "price": ("Price/hr",  100),
    "slots": ("Slots",      70),
    "status":("Status",     80),
}
```

### Row Values
```python
for t in turfs:
    status_text = "Active" if t["is_active"] else "Inactive"
    tree.insert("", "end", iid=t["id"], values=(
        t["name"], t["sport"], t["area"],
        f"₹{t['price_per_hour']:,.0f}",
        t["available_slots"], status_text
    ))
```

### Edit Button — `on_edit()`
```python
def on_edit():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Select Turf", "Please select a turf to edit.")
        return
    turf_id = int(selected[0])
    turf = database.get_turf_by_id(turf_id)
    dashboard.add_turf_tab.load_turf_for_edit(turf)
    dashboard.notebook.select(dashboard.add_turf_tab.frame)
```

### Delete Button — `on_delete()`
```python
def on_delete():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Select Turf", "Please select a turf to delete.")
        return
    turf_id = int(selected[0])
    if messagebox.askyesno("Confirm Delete",
            "Delete this turf? Existing bookings will not be affected."):
        database.soft_delete_turf(turf_id)
        messagebox.showinfo("Deleted", "Turf removed from listings.")
        load_turfs()
```

---

## `admin/manage_bookings.py` — Manage Bookings Tab

### Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  Booking Requests                              [🔄 Refresh]          │
├─────────────────────────────────────────────────────────────────────┤
│  Filter: Status [All ▼]   Turf [All ▼]                              │
├─────────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ Customer │ Turf │ Sport │ Date │ Time │ Amount │ Status │ Pay │  │
│  ├──────────┼──────┼───────┼──────┼──────┼────────┼────────┼─────┤  │
│  │ John Doe │ Goal │  ⚽   │10/04 │08-10 │ ₹1400  │Pending │Paid │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                       │
│  [✅ Accept Booking]              [❌ Reject Booking]                │
└─────────────────────────────────────────────────────────────────────┘
```

### Treeview Columns
```python
columns = ("customer","turf","sport","date","time","amount","status","payment")
column_config = {
    "customer": ("Customer",  150),
    "turf"    : ("Turf",      170),
    "sport"   : ("Sport",     100),
    "date"    : ("Date",       90),
    "time"    : ("Time",      110),
    "amount"  : ("Amount",     90),
    "status"  : ("Status",     90),
    "payment" : ("Payment",    80),
}
```

### Status Filter Dropdown
```python
status_var = tk.StringVar(value="All")
status_filter = ttk.Combobox(
    filter_bar, textvariable=status_var,
    values=["All","Pending","Confirmed","Rejected","Cancelled"],
    state="readonly", width=15
)
status_filter.bind("<<ComboboxSelected>>", lambda e: load_bookings())
```

### Load Bookings — `load_bookings()`
```python
def load_bookings():
    for row in tree.get_children():
        tree.delete(row)
    all_bookings = database.get_bookings_by_owner(session.get_user_id())
    status_filter_val = status_var.get()
    turf_filter_val   = turf_var.get()

    for b in all_bookings:
        if status_filter_val != "All" and b["status"] != status_filter_val:
            continue
        if turf_filter_val != "All" and b["turf_name"] != turf_filter_val:
            continue
        time_str = f"{b['start_time']} – {b['end_time']}"
        tree.insert("", "end", iid=b["id"], values=(
            b["customer_name"], b["turf_name"], b["sport"],
            b["booking_date"], time_str,
            f"₹{b['total_price']:,.0f}", b["status"], b["payment_status"]
        ), tags=(b["status"],))
```

### Accept Button — `on_accept()`
```python
def on_accept():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Select Booking", "Please select a booking.")
        return
    booking_id = int(selected[0])
    booking = database.get_booking_by_id(booking_id)
    if booking["status"] != "Pending":
        messagebox.showerror("Cannot Accept",
            "Only Pending bookings can be accepted.")
        return
    database.update_booking_status(booking_id, "Confirmed")
    database.decrement_slots(booking["turf_id"])
    messagebox.showinfo("Accepted", "Booking confirmed! Slot reserved.")
    load_bookings()
```

### Reject Button — `on_reject()`
```python
def on_reject():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Select Booking", "Please select a booking.")
        return
    booking_id = int(selected[0])
    booking = database.get_booking_by_id(booking_id)
    if booking["status"] != "Pending":
        messagebox.showerror("Cannot Reject",
            "Only Pending bookings can be rejected.")
        return
    reason = simpledialog.askstring(
        "Rejection Reason",
        "Optional: Enter reason for rejection (shown to customer):"
    )
    database.update_booking_status(booking_id, "Rejected")
    messagebox.showinfo("Rejected", "Booking has been rejected.")
    load_bookings()
```

---

## `admin/revenue.py` — Revenue Dashboard Tab

### Layout

```
┌────────────────────────────────────────────────────────────────────┐
│  Revenue Dashboard                               [🔄 Refresh]       │
├─────────────────────────────────────┬──────────────────────────────┤
│  SUMMARY CARDS (top row)            │                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                           │
│  │Total Rev │ │Total Bkgs│ │ Turfs   │                            │
│  │₹24,500   │ │   18     │ │   5     │                            │
│  └──────────┘ └──────────┘ └──────────┘                           │
├────────────────────────────────────────────────────────────────────┤
│  MATPLOTLIB BAR CHART — Revenue per Turf                           │
│  (Embedded FigureCanvasTkAgg)                                       │
│                                                                     │
│  [Bar chart: X=turf names, Y=revenue in ₹]                        │
│  Bar color: #1a472a gradient, labels on top of bars                │
└────────────────────────────────────────────────────────────────────┘
```

### Summary Cards — `render_summary()`
```python
def render_summary():
    revenue_data = database.get_revenue_by_turf(session.get_user_id())
    total_revenue = sum(r[1] for r in revenue_data)
    bookings = database.get_bookings_by_owner(session.get_user_id())
    total_bookings = len(bookings)
    total_turfs = len(database.get_turfs_by_owner(session.get_user_id()))

    cards = [
        ("Total Revenue", f"₹{total_revenue:,.0f}", "#1a472a"),
        ("Total Bookings", str(total_bookings),      "#1565c0"),
        ("Active Turfs",   str(total_turfs),         "#e65100"),
    ]
    for title, value, color in cards:
        card = tk.Frame(card_row, bg=color, padx=20, pady=15)
        tk.Label(card, text=title, bg=color, fg="white",
                 font=("Arial",10)).pack()
        tk.Label(card, text=value, bg=color, fg="#f0a500",
                 font=("Arial",20,"bold")).pack()
        card.pack(side="left", padx=10)
```

### Matplotlib Chart — `render_chart()`
```python
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

def render_chart():
    revenue_data = database.get_revenue_by_turf(session.get_user_id())
    if not revenue_data:
        no_data_label.pack()
        return

    names    = [r[0] for r in revenue_data]
    amounts  = [r[1] for r in revenue_data]

    fig = Figure(figsize=(8, 4), dpi=100)
    ax  = fig.add_subplot(111)
    bars = ax.bar(names, amounts, color="#1a472a", edgecolor="#0d3320")

    # Value labels on top of bars
    for bar, amount in zip(bars, amounts):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 50,
            f"₹{amount:,.0f}",
            ha="center", va="bottom", fontsize=9, fontweight="bold"
        )

    ax.set_title("Revenue by Turf (Paid Bookings)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Turf Name", fontsize=10)
    ax.set_ylabel("Revenue (₹)", fontsize=10)
    ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
```
