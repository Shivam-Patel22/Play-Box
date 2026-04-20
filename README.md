![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)
![Version](https://img.shields.io/badge/version-1.0.0-orange)

# PlayBox

**PlayBox:** Your all-in-one platform for seamless sports turf booking and management.

PlayBox (formerly Turf Space) is a robust web application built to connect sport enthusiasts with turf owners. It streamlines the process of discovering, booking, and managing sports venues. Customers can dynamically search for turfs based on location, sport type, and available time slots, while administrators are equipped with a comprehensive dashboard to manage listings, track income, and handle booking requests.

## Features

**Core Features**
- **User Authentication:** Secure signup and login distinct workflows for 'Customer' and 'Admin' roles.
- **Dynamic Search & Filtering:** Customers can easily search turfs by name, location, area, and specific sports type.
- **Real-Time Availability:** Dynamic time slot validation prevents overlapping bookings or booking past hours/dates.

**Admin Features**
- **Turf Management:** Administrators can add, edit, or delete turf listings along with descriptions, pricing, and dynamic photo uploads.
- **Booking Oversight:** Accept, reject, or track pending booking requests from customers. 
- **Revenue Analytics:** Visual revenue tracking metrics and charts to monitor booking income and total bookings.

**Upcoming/Planned Features**
- Integration with third-party payment gateways (e.g., Stripe or Razorpay or equivalent).
- Automated email or SMS notifications for confirmed or rejected bookings.

## File structure

```text
turf_website/
├── app.py
├── turf_booking.db
├── static/
│   ├── style.css
│   └── uploads/
└── templates/
    ├── add_turf.html
    ├── admin_dashboard.html
    ├── base.html
    ├── book.html
    ├── customer_dashboard.html
    ├── edit_turf.html
    ├── index.html
    ├── login.html
    ├── manage_bookings.html
    ├── my_bookings.html
    ├── revenue.html
    └── signup.html
```

- **`app.py`**: The core Flask application file containing all routing logic, authentication flows, database interactions, and business rules.
- **`turf_booking.db`**: The SQLite database file handling persistent data storage for users, turfs, bookings, and payments.
- **`static/`**: Holds static assets; `style.css` contains all the stylesheet definitions, and the `uploads/` directory stores user-uploaded turf images.
- **`templates/`**: Contains the Jinja2 HTML templates. `base.html` serves as the layout wrapper for role-specific pages like `customer_dashboard.html` and `admin_dashboard.html`.

## Setup & installation

Follow these steps to get PlayBox running locally.

**1. Prerequisites**
Ensure you have Python 3.8+ installed on your system.

**2. Clone the repository**
```bash
git clone https://github.com/your-username/playbox.git
cd playbox/turf_website
```

**3. Install dependencies**
It is recommended to use a virtual environment before installing the requirements. In case your repository lacks a `requirements.txt`, install Flask directly.
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install Flask
```

**4. Configure the environment**
Create your `.env` file (see Environment variables section below) to safely load specific variables, if desired.

**5. Running in development mode**
This will automatically launch the database bootstrap (`init_db()`) and start the local development server on port 5000.
```bash
# Ensure you are inside turf_website directory
python app.py
```

**6. Running in production mode**
For a production environment, avoid the Flask built-in server. Instead, use a robust WSGI server like Waitress (Windows) or Gunicorn (Linux/macOS).
```bash
# Example using Gunicorn (Linux/macOS)
pip install gunicorn
gunicorn -w 4 -b 127.0.0.1:5000 app:app
```

## Environment variables

| Variable | Description | Example value | Required |
|----------|-------------|---------------|----------|
| `FLASK_APP` | The entry point to the application | `app.py` | No (default) |
| `FLASK_ENV` | Specifies the environment type | `development` | No |
| `SECRET_KEY` | Flask session secure key for hashing | `super-secret-key-xyz` | Yes (for prod) |
| `FLASK_RUN_PORT`| The port the application will bind to | `5000` | No |

**How to create a `.env` file**
1. At the root of the `turf_website` folder, create a new file named `.env`.
2. Open it and define your key-value pairs without quotes around strings:
```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=my_secure_randomly_generated_string
```
*(Note: To integrate this automatically, you may consider importing `python-dotenv` into `app.py`).*

## Usage guide

**1. Customer Workflow**
- Navigate to the `Signup` page and register as a **Customer**.
- Once logged in, you'll be redirected to the customer dashboard where you can filter turfs.
- Click **"Book Turf"** on any available listing. Choose a start and end time.
![Customer Booking Placeholder](https://via.placeholder.com/600x300.png?text=Screenshot:+Customer+Booking+Screen)

**2. Admin Workflow**
- Navigate to the `Signup` page and register as an **Admin** (or use the seeded system admin at `admin@turfbooking.com`).
- On the Admin Dashboard, click **"Add Turf"** to initialize a new slot.
- Upload turf photos; these are dynamically stored in the `/static/uploads` directory.
- Review bookings under **"Manage Bookings"**, and securely `Accept` or `Reject` prospective customer requests.

```python
# Example: Seeded super admin login credentials
Email: admin@turfbooking.com
Password: admin123
```

## License

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)

This project is licensed under the MIT License.
**Summary:** It allows for free commercial use, modification, distribution, and private use, provided that the original copyright notice remains.

***

**Developer Note:** Please review and fill in the following before finalizing:
- Replace the `[your-username]` repository link in the cloning instructions with your actual GitHub repo URL.
- Update the screenshot placeholder links in the **Usage guide** with the real live application screenshots.
- Change/update the `.env` instructions if you plan to introduce external dependency plugins like `python-dotenv`.
- Ensure you change the hardcoded `app.secret_key` in `app.py` to draw exclusively from the environment for production safety.
