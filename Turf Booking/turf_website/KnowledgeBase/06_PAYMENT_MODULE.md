# 06 — Payment Module Specification
## File: `customer/payment.py`

---

## `PaymentDialog(parent, booking_id, turf, total_price)` — Toplevel

### Window Properties
```
Title    : Complete Payment — TurfBook Pro
Size     : 500 × 580
Resizable: False
Modal    : Yes (grab_set)
bg       : #ffffff
```

---

## Layout

```
┌──────────────────────────────────────────────────────┐
│  💳 Complete Your Payment                            │  ← header bar #1a472a
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │  ORDER SUMMARY                                │   │
│  │  Turf   : Goal Zone Football Arena            │   │
│  │  Sport  : Football                            │   │
│  │  Date   : 2025-04-10                          │   │
│  │  Time   : 08:00 – 10:00                       │   │
│  │  ─────────────────────────────────────────    │   │
│  │  Amount Due:  ₹1,400.00                       │   │  ← large gold text
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  Select Payment Method:                              │
│                                                      │
│  ┌──────────┐ ┌──────────┐ ┌───────────┐ ┌──────┐  │
│  │  📱 UPI  │ │💳 Credit │ │💳 Debit  │ │🏦 Net│  │
│  │          │ │  Card    │ │  Card     │ │Banking│  │
│  └──────────┘ └──────────┘ └───────────┘ └──────┘  │
│                                                      │
│  ──── UPI Payment ────────────────────────────────  │
│  UPI ID:  [________________________________]         │
│            (e.g. yourname@upi)                       │
│                                                      │
│  [ 🔒 Pay ₹1,400.00 Securely ]                      │  ← primary button
│                                                      │
│  🔒 Secured by TurfBook Pro · All data encrypted    │
└──────────────────────────────────────────────────────┘
```

---

## Payment Method Tabs (toggle frames)

Use four `tk.Frame` panels. Only one is visible at a time.
Selecting a method button hides others and shows the relevant form.

### UPI Panel
```
Widgets:
  Label    : "UPI ID"
  Entry    : upi_id_entry (placeholder: "yourname@upi")
  Label    : "Ensure your UPI app is open to approve the payment."
Validation:
  - Non-empty
  - Matches r'^[\w.\-]+@[\w]+$'
```

### Credit Card Panel
```
Widgets:
  Label  : "Cardholder Name"
  Entry  : cardholder_name
  Label  : "Card Number"
  Entry  : card_number  (max 16 digits, show="*" after first 4)
  Label  : "Expiry (MM/YY)"
  Entry  : expiry
  Label  : "CVV"
  Entry  : cvv  (show="●", max 3 digits)
Validation:
  - Name  : non-empty
  - Card  : exactly 16 digits
  - Expiry: matches r'^\d{2}/\d{2}$', not expired
  - CVV   : exactly 3 digits
```

### Debit Card Panel
```
Same layout as Credit Card Panel (reuse same widget logic).
```

### Net Banking Panel
```
Widgets:
  Label    : "Select Bank"
  Combobox : bank_var — values = [
               "State Bank of India", "HDFC Bank", "ICICI Bank",
               "Axis Bank", "Kotak Mahindra Bank", "Punjab National Bank",
               "Bank of Baroda", "Canara Bank", "Union Bank of India",
               "Yes Bank"
             ]
  Label    : "Account Number"
  Entry    : account_number
  Label    : "IFSC Code"
  Entry    : ifsc
Validation:
  - Bank    : must select one
  - Account : non-empty, 9-18 digits
  - IFSC    : matches r'^[A-Z]{4}0[A-Z0-9]{6}$'
```

---

## Method Selector Buttons

Four styled `tk.Button` widgets. Selected method has a distinct "active" style:

```python
METHODS = [
    ("📱 UPI",         "UPI"),
    ("💳 Credit Card", "Credit Card"),
    ("💳 Debit Card",  "Debit Card"),
    ("🏦 Net Banking", "Net Banking"),
]

def select_method(method_name):
    payment_method_var.set(method_name)
    for btn in method_buttons:
        if btn.method_name == method_name:
            btn.config(bg="#1a472a", fg="white", relief="solid")
        else:
            btn.config(bg="#f5f5f5", fg="#333333", relief="flat")
    show_method_panel(method_name)
```

Default selected method: `"UPI"`.

---

## `on_pay_click()` — Payment Handler

```python
def on_pay_click():
    method = payment_method_var.get()
    errors = validate_payment_fields(method)
    if errors:
        messagebox.showerror("Invalid Details", "\n".join(errors))
        return

    # Simulate processing
    processing_dialog = show_processing_popup()

    # Generate transaction ID
    import random, string
    txn_id = "TXN" + "".join(
        random.choices(string.ascii_uppercase + string.digits, k=12)
    )

    # Simulate 1.5 second delay (use root.after)
    def complete_payment():
        processing_dialog.destroy()

        # Save to database
        database.create_payment(
            booking_id   = booking_id,
            customer_id  = session.get_user_id(),
            amount       = total_price,
            method       = method,
            transaction_id = txn_id,
        )
        database.update_payment_status(booking_id)

        # Close payment dialog
        self.destroy()

        # Show receipt
        show_receipt(txn_id, method, total_price)

    self.after(1500, complete_payment)
```

---

## Processing Popup — `show_processing_popup()`

```
┌──────────────────────────────────┐
│                                  │
│         ⏳ Processing...         │
│   Please wait while we verify   │
│        your payment.             │
│                                  │
│   [████████████░░░░░░] 65%       │  ← animated progress bar (ttk.Progressbar)
│                                  │
└──────────────────────────────────┘

Size     : 340 × 180
Resizable: False
No close button (overrideredirect or disabled protocol)
Progress bar mode: "indeterminate", starts automatically
```

```python
def show_processing_popup():
    popup = tk.Toplevel(self)
    popup.title("")
    popup.geometry("340x180")
    popup.resizable(False, False)
    popup.grab_set()
    center_window(popup, 340, 180)
    popup.protocol("WM_DELETE_WINDOW", lambda: None)  # disable close

    tk.Label(popup, text="⏳ Processing Payment...",
             font=("Arial",13,"bold")).pack(pady=(30,10))
    tk.Label(popup, text="Please wait while we verify your payment.",
             font=("Arial",10), fg="#666").pack()
    bar = ttk.Progressbar(popup, mode="indeterminate", length=260)
    bar.pack(pady=20)
    bar.start(12)
    return popup
```

---

## Receipt Popup — `show_receipt(txn_id, method, amount)`

```
┌─────────────────────────────────────────────┐
│  ✅  Payment Successful!                    │  ← header bg=#2e7d32, white text
├─────────────────────────────────────────────┤
│                                             │
│  🎉 Your booking is confirmed!              │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │  RECEIPT                            │   │
│  │  Transaction ID : TXN4XR9K2PQM1Z   │   │
│  │  Turf           : Goal Zone Arena   │   │
│  │  Sport          : Football          │   │
│  │  Date           : 2025-04-10        │   │
│  │  Time           : 08:00 – 10:00     │   │
│  │  Payment Method : UPI               │   │
│  │  Amount Paid    : ₹1,400.00         │   │
│  │  Status         : PAID ✅           │   │
│  │  Timestamp      : 2025-04-09 14:32  │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  [ 📋 Copy Transaction ID ]   [ ✖ Close ]  │
└─────────────────────────────────────────────┘

Size: 460 × 500
```

### Copy Transaction ID Button
```python
def copy_txn():
    self.clipboard_clear()
    self.clipboard_append(txn_id)
    messagebox.showinfo("Copied", "Transaction ID copied to clipboard!")
```

---

## `generate_transaction_id() → str` (in `utils.py`)

```python
import random, string

def generate_transaction_id() -> str:
    chars = string.ascii_uppercase + string.digits
    return "TXN" + "".join(random.choices(chars, k=12))
```

Example output: `TXNA3K9ZBQ2PXN4`

---

## Payment Validation Rules

| Method | Field | Rule |
|--------|-------|------|
| UPI | UPI ID | Non-empty, matches `r'^[\w.\-]+@[\w]+$'` |
| Credit/Debit Card | Cardholder Name | Non-empty, letters only |
| Credit/Debit Card | Card Number | Exactly 16 digits |
| Credit/Debit Card | Expiry | Matches `MM/YY`, not expired |
| Credit/Debit Card | CVV | Exactly 3 digits |
| Net Banking | Bank | Must be selected |
| Net Banking | Account No. | 9–18 digits |
| Net Banking | IFSC | Matches `r'^[A-Z]{4}0[A-Z0-9]{6}$'` |
