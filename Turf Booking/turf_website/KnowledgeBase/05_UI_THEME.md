# 05 — UI Theme & Style Specification

---

## Colour Palette

| Name | Hex | Usage |
|------|-----|-------|
| Primary Dark Green | `#1a472a` | Header, buttons, badges |
| Primary Deeper | `#0d3320` | Admin header, hover states |
| Accent Gold | `#f0a500` | App title, price display, highlights |
| Light Green | `#c8e6c9` | Subtext on dark backgrounds |
| Success Green | `#2e7d32` | Confirmed status, Cricket badge |
| Danger Red | `#c0392b` | Logout button, errors |
| Warning Orange | `#e65100` | Pickleball badge |
| Blue | `#1565c0` | Football badge, info cards |
| Purple | `#4a148c` | Pool badge |
| Pink | `#880e4f` | Snooker badge |
| White | `#ffffff` | Card backgrounds, text on dark |
| Light Grey | `#f5f5f5` | App background |
| Mid Grey | `#666666` | Secondary text |
| Dark Grey | `#333333` | Primary body text |
| Pending Yellow | `#fff9c4` | Pending booking row |
| Confirmed Green | `#c8e6c9` | Confirmed booking row |
| Rejected Red | `#ffcdd2` | Rejected booking row |

---

## Typography

| Element | Font | Size | Weight |
|---------|------|------|--------|
| App Title | Arial | 22 | Bold |
| Dashboard Title | Arial | 18 | Bold |
| Section Header | Arial | 14 | Bold |
| Card Title | Arial | 13 | Bold |
| Body Text | Arial | 11 | Normal |
| Small / Caption | Arial | 9 | Normal |
| Price Display | Arial | 14 | Bold |
| Button Text | Arial | 11 | Bold |
| Tab Label | Arial | 10 | Normal |

---

## Global `ttk.Style` Configuration

Apply in `main.py` before launching any window:

```python
import tkinter.ttk as ttk

def apply_global_style(root):
    style = ttk.Style(root)
    style.theme_use("clam")   # Use "clam" as base (most consistent cross-platform)

    # ── Notebook (tab container) ──────────────────────────────────
    style.configure("TNotebook",
        background="#f5f5f5",
        tabmargins=[2, 5, 2, 0]
    )
    style.configure("TNotebook.Tab",
        background="#e0e0e0",
        foreground="#333333",
        font=("Arial", 10),
        padding=[14, 8]
    )
    style.map("TNotebook.Tab",
        background=[("selected", "#1a472a"), ("active", "#2e7d32")],
        foreground=[("selected", "#ffffff"), ("active", "#ffffff")],
    )

    # ── Treeview ──────────────────────────────────────────────────
    style.configure("Treeview",
        background="#ffffff",
        foreground="#333333",
        rowheight=30,
        fieldbackground="#ffffff",
        font=("Arial", 10),
    )
    style.configure("Treeview.Heading",
        background="#1a472a",
        foreground="#ffffff",
        font=("Arial", 10, "bold"),
        relief="flat",
    )
    style.map("Treeview",
        background=[("selected", "#1a472a")],
        foreground=[("selected", "#ffffff")],
    )

    # ── Entry Fields ──────────────────────────────────────────────
    style.configure("TEntry",
        padding=[8, 6],
        font=("Arial", 11),
        fieldbackground="#ffffff",
        bordercolor="#cccccc",
    )

    # ── Combobox ──────────────────────────────────────────────────
    style.configure("TCombobox",
        padding=[8, 6],
        font=("Arial", 11),
    )
    style.map("TCombobox",
        fieldbackground=[("readonly", "#ffffff")],
    )

    # ── Scrollbar ────────────────────────────────────────────────
    style.configure("TScrollbar",
        background="#cccccc",
        troughcolor="#f5f5f5",
        arrowcolor="#1a472a",
    )

    # ── Separator ────────────────────────────────────────────────
    style.configure("TSeparator", background="#e0e0e0")
```

---

## Reusable Widget Helpers (in `utils.py`)

### `make_button(parent, text, command, style="primary", **kwargs) → tk.Button`
```python
BUTTON_STYLES = {
    "primary" : {"bg": "#1a472a", "fg": "#ffffff", "activebackground": "#0d3320"},
    "danger"  : {"bg": "#c0392b", "fg": "#ffffff", "activebackground": "#922b21"},
    "secondary":{"bg": "#7f8c8d", "fg": "#ffffff", "activebackground": "#616a6b"},
    "warning" : {"bg": "#e65100", "fg": "#ffffff", "activebackground": "#bf360c"},
    "success" : {"bg": "#2e7d32", "fg": "#ffffff", "activebackground": "#1b5e20"},
    "gold"    : {"bg": "#f0a500", "fg": "#1a472a", "activebackground": "#d4920a"},
}

def make_button(parent, text, command, style="primary", **kwargs):
    cfg = BUTTON_STYLES.get(style, BUTTON_STYLES["primary"])
    return tk.Button(
        parent,
        text=text,
        command=command,
        font=("Arial", 11, "bold"),
        cursor="hand2",
        relief="flat",
        padx=16, pady=8,
        borderwidth=0,
        activeforeground=cfg["fg"],
        **cfg,
        **kwargs,
    )
```

### `make_label(parent, text, style="body", **kwargs) → tk.Label`
```python
LABEL_STYLES = {
    "title"  : {"font": ("Arial", 22, "bold"), "fg": "#f0a500"},
    "heading": {"font": ("Arial", 14, "bold"), "fg": "#333333"},
    "subhead": {"font": ("Arial", 11, "bold"), "fg": "#1a472a"},
    "body"   : {"font": ("Arial", 11),         "fg": "#333333"},
    "caption": {"font": ("Arial",  9),         "fg": "#666666"},
    "on_dark": {"font": ("Arial", 11),         "fg": "#c8e6c9"},
}
def make_label(parent, text, style="body", **kwargs):
    cfg = LABEL_STYLES.get(style, LABEL_STYLES["body"])
    return tk.Label(parent, text=text, **cfg, **kwargs)
```

### `make_section_header(parent, text) → tk.Frame`
Returns a full-width frame with a left-colored bar and heading label:
```python
def make_section_header(parent, text):
    frame = tk.Frame(parent, bg="#f5f5f5")
    bar = tk.Frame(frame, bg="#1a472a", width=4)
    bar.pack(side="left", fill="y", padx=(0,10))
    lbl = tk.Label(frame, text=text,
                   font=("Arial",13,"bold"), fg="#1a472a", bg="#f5f5f5")
    lbl.pack(side="left")
    return frame
```

---

## Card Style Rules

All turf cards follow these rules:
```python
card = tk.Frame(
    parent,
    bg="#ffffff",
    relief="flat",
    bd=1,
    highlightthickness=1,
    highlightbackground="#e0e0e0",
    highlightcolor="#1a472a",
    padx=15,
    pady=15,
    cursor="hand2",
)
# Hover effect:
card.bind("<Enter>", lambda e: card.config(highlightbackground="#1a472a", bd=2))
card.bind("<Leave>", lambda e: card.config(highlightbackground="#e0e0e0", bd=1))
```

---

## Window Centering

```python
def center_window(window, width, height):
    window.update_idletasks()
    sw = window.winfo_screenwidth()
    sh = window.winfo_screenheight()
    x  = (sw - width)  // 2
    y  = (sh - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")
```

---

## Separator Line (horizontal rule)

```python
def add_separator(parent):
    sep = ttk.Separator(parent, orient="horizontal")
    sep.pack(fill="x", pady=10)
```

---

## Status Badge Widget

```python
STATUS_BADGE_COLORS = {
    "Pending"  : ("#fff9c4", "#f57f17"),
    "Confirmed": ("#c8e6c9", "#2e7d32"),
    "Rejected" : ("#ffcdd2", "#c62828"),
    "Cancelled": ("#f5f5f5", "#616161"),
    "Paid"     : ("#e8f5e9", "#1b5e20"),
    "Unpaid"   : ("#fff3e0", "#e65100"),
}

def status_badge(parent, status_text):
    bg, fg = STATUS_BADGE_COLORS.get(status_text, ("#e0e0e0","#333333"))
    return tk.Label(parent, text=status_text,
                    bg=bg, fg=fg,
                    font=("Arial", 9, "bold"),
                    padx=8, pady=3, relief="flat")
```

---

## Messagebox Patterns

Always use these consistently:
```python
# Success
messagebox.showinfo("Success", "Your message here.")

# Error
messagebox.showerror("Error", "Something went wrong.")

# Warning
messagebox.showwarning("Warning", "Please check your input.")

# Confirmation (returns True/False)
if messagebox.askyesno("Confirm", "Are you sure?"):
    ...
```

---

## Scrollable Frame Pattern (reusable)

```python
def make_scrollable_frame(parent):
    """Returns (outer_frame, inner_frame, canvas)."""
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

    # Mouse wheel binding
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)      # Windows
    canvas.bind_all("<Button-4>",
        lambda e: canvas.yview_scroll(-1, "units"))       # Linux scroll up
    canvas.bind_all("<Button-5>",
        lambda e: canvas.yview_scroll( 1, "units"))       # Linux scroll down

    return outer, inner, canvas
```
