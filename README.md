# 🏢 SmartBuilding — Society Management System

A full-stack **Django** web application for managing residential housing societies. It provides a centralized digital dashboard where residents, security staff, and the secretary can access building facilities, complaints, notices, visitor management, amenity booking, and more — all from a single login.

---

## 📌 Objective

Managing a housing society involves coordinating dozens of services — water supply, electricity, gas, parking, gym memberships, maintenance payments, visitor management, and emergency contacts. Traditionally this is handled through paper notices, WhatsApp groups, and word-of-mouth, which is unreliable and scattered.

**SmartBuilding** solves this by providing:

- A **single web portal** accessible from any device (phone, tablet, laptop).
- **Role-based signup** (Security, Secretary, Flat Owner) so the right people see the right information.
- A **dashboard** with quick-action cards to navigate to every service the society offers.
- **Complaint management** with auto-generated ticket numbers and status tracking.
- **Digital notice board** for society-wide announcements with urgent flagging.
- **Visitor pre-approval** system with security gate view.
- **Amenity booking** with double-booking prevention.
- **Real-time facility data** — water tank levels, electricity bills, gas bills, WiFi usage, plumbing complaints, and sewage treatment status.
- **Emergency contact directory** with one-tap calling for fire brigade, police, ambulance, etc.

---

## 🏗️ Architecture & Flow

```
┌─────────────────────────────────────────────────────────┐
│                     USER (Browser)                      │
│         Phone / Tablet / Laptop / Desktop               │
└──────────────────────┬──────────────────────────────────┘
                       │  HTTP Request
                       ▼
┌─────────────────────────────────────────────────────────┐
│              Django Development Server                  │
│              http://127.0.0.1:8000                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  urls.py  ──►  Routes every URL to the correct view     │
│                (30+ URL patterns)                       │
│                                                         │
│  ┌────────────────────────────────────────────────────┐  │
│  │                   views.py                         │  │
│  │                                                    │  │
│  │  ── Auth ──────────────────────────────────────    │  │
│  │  signup()           → User registration            │  │
│  │  login_view()       → Session-based login          │  │
│  │  logout_view()      → Clear session & redirect     │  │
│  │                                                    │  │
│  │  ── Dashboard ─────────────────────────────────    │  │
│  │  dashboard()        → Main hub + profile modal     │  │
│  │  dashboard_page()   → 9 sub-pages (facilities,     │  │
│  │                       contact, events, parking,    │  │
│  │                       apartment, maintenance,      │  │
│  │                       gym, flat_sales, info)       │  │
│  │  facility_detail()  → Individual facility reports  │  │
│  │                                                    │  │
│  │  ── Complaints ────────────────────────────────    │  │
│  │  complaints()       → Submit + view own tickets    │  │
│  │  all_complaints()   → Secretary: manage all        │  │
│  │  update_complaint() → Secretary: change status     │  │
│  │                                                    │  │
│  │  ── Notices ───────────────────────────────────    │  │
│  │  notice_board()     → View all active notices      │  │
│  │  post_notice()      → Secretary: create notice     │  │
│  │  delete_notice()    → Secretary: soft-delete        │  │
│  │                                                    │  │
│  │  ── Visitors ──────────────────────────────────    │  │
│  │  visitor_pass()     → Flat Owner: pre-approve      │  │
│  │  cancel_visitor()   → Flat Owner: cancel pass      │  │
│  │  security_visitors()→ Security: today's visitors   │  │
│  │  mark_arrived()     → Security: check-in visitor   │  │
│  │                                                    │  │
│  │  ── Amenity Booking ───────────────────────────    │  │
│  │  book_amenity()     → Book + view own bookings     │  │
│  │  cancel_booking()   → Cancel upcoming booking      │  │
│  │  all_bookings()     → Secretary: view all          │  │
│  └────────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────┐    ┌──────────────────────────────┐   │
│  │  models.py   │    │  forms.py                    │   │
│  │  (5 models)  │    │                              │   │
│  │              │    │  SignupForm  (registration)  │   │
│  │  Signup      │    │  LoginForm   (authentication)│   │
│  │  Complaint   │    │  ProfileForm (photo upload)  │   │
│  │  Notice      │    └──────────────────────────────┘   │
│  │  VisitorPass │                                       │
│  │  Amenity     │    ┌──────────────────────────────┐   │
│  │   Booking    │    │  Templates (13 HTML files)   │   │
│  └──────┬───────┘    └──────────────────────────────┘   │
│         │                                               │
│         ▼                                               │
│  ┌──────────────┐                                       │
│  │  SQLite DB   │                                       │
│  │  db.sqlite3  │                                       │
│  └──────────────┘                                       │
└─────────────────────────────────────────────────────────┘
```

### Request Flow (Step-by-Step)

1. **User opens** `http://127.0.0.1:8000/signup/` in a browser.
2. **Django URL router** (`urls.py`) matches the path and calls `signup()` in `views.py`.
3. The view renders `signup_page.html` with the `SignupForm`.
4. On form submission, the data is validated, the **password is hashed**, and a new `Signup` record is saved to the **SQLite database**.
5. After login, a **session cookie** (`user_id`) is stored so the user stays logged in.
6. The **dashboard** reads the session, fetches the user from the DB, and renders quick-action cards.
7. Each card links to a **sub-page** (e.g., `/complaints/`) with detailed data.
8. **Logout** clears the session and redirects to login.

---

## ✨ Features

### Core Modules

| Module | What It Does |
|--------|-------------|
| **Signup** | Register as Security, Secretary, or Flat Owner with Aadhar & contact validation |
| **Login / Logout** | Session-based authentication with hashed passwords and secure logout |
| **Dashboard** | Central hub with profile modal, photo upload, and 13+ quick-action cards |

### Building & Facility Management

| Module | What It Does |
|--------|-------------|
| **Facilities** | Water tank levels, electricity bills, gas bills, WiFi usage, plumbing complaints, sewage status |
| **Contact** | Emergency numbers (fire, police, ambulance, lift, gas, cleaning, etc.) with one-tap calling |
| **Events** | Indian festival calendar with celebration ideas for the society |
| **Info** | Society name, address, registration number, committee members |
| **Parking** | Parking rules, slot allocation table, EV charger points |
| **Apartment** | Full directory of flats — owner name, contact, email, vehicle number |
| **Maintenance** | Quarterly maintenance amount, due dates, late fees, payment modes |
| **Gym** | Gym info, timings, trainer details, equipment list, member registry |
| **Flat Sales** | Listings of flats available for sale/resale with prices |

### 🆕 Advanced Features

| Module | What It Does |
|--------|-------------|
| **🔧 Complaint Management** | File complaints with auto-generated TKT-XXXX ticket numbers. Track status (Pending → In Progress → Resolved). Secretary can manage all complaints with inline status updates and remarks. |
| **📋 Digital Notice Board** | Secretary posts announcements visible to all residents. Supports categories (General, Emergency, Meeting, etc.) and urgent flagging with red highlight. Soft-delete for notices. |
| **🚗 Visitor Pre-Approval** | Flat Owners pre-register expected visitors with date, time, flat number, and vehicle. Security sees today's visitors at the gate and marks them as "Arrived". Auto-expires past visitors. |
| **🏊 Amenity Booking** | Book shared amenities (Community Hall, Terrace, BBQ Area, Swimming Pool, Conference Room) with morning/afternoon/evening slots. Double-booking prevention. Cancel upcoming bookings. Secretary sees all bookings with filters. |

---

## 👥 Roles & Permissions

| Feature | Security | Secretary | Flat Owner |
|---------|----------|-----------|------------|
| View Dashboard | ✅ | ✅ | ✅ |
| File Complaints | ✅ | ✅ | ✅ |
| View Notice Board | ✅ | ✅ | ✅ |
| Book Amenities | ✅ | ✅ | ✅ |
| Post / Delete Notices | ❌ | ✅ | ❌ |
| Manage All Complaints | ❌ | ✅ | ❌ |
| View All Bookings | ❌ | ✅ | ❌ |
| Pre-Approve Visitors | ❌ | ❌ | ✅ |
| Gate View (Today's Visitors) | ✅ | ❌ | ❌ |
| Mark Visitor Arrived | ✅ | ❌ | ❌ |
| View All Visitors | ❌ | ✅ | ❌ |
| Logout | ✅ | ✅ | ✅ |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.x, Django 5.2.8 |
| **Frontend** | HTML5, CSS3 (inline + embedded), vanilla JavaScript |
| **Database** | SQLite 3 (file-based, zero config) |
| **Auth** | Django session framework + `django.contrib.auth.hashers` |
| **Image Handling** | Pillow (for profile photo uploads) |
| **Styling** | Glassmorphism UI with gradient backgrounds, responsive grid layout |

---

## 📁 Folder Structure

```
Ram College Project/
├── env/                          # Python virtual environment
└── smartbuilding/                # Django project root
    ├── manage.py                 # Django CLI entry point
    ├── requirements.txt          # Python dependencies
    ├── db.sqlite3                # SQLite database file
    ├── media/                    # User-uploaded files (profile images)
    │   └── profiles/
    ├── static_root/              # Collected static files (for production)
    │
    ├── smartbuilding/            # Django project settings package
    │   ├── __init__.py
    │   ├── settings.py           # All Django configuration
    │   ├── urls.py               # Root URL routing (30+ patterns)
    │   ├── wsgi.py               # WSGI entry point
    │   └── asgi.py               # ASGI entry point
    │
    └── bot/                      # Main application
        ├── __init__.py
        ├── models.py             # 5 models (Signup, Complaint, Notice,
        │                         #   VisitorPass, AmenityBooking)
        ├── forms.py              # SignupForm, LoginForm, ProfileForm
        ├── views.py              # 20+ view functions (business logic)
        ├── admin.py              # Django admin config
        ├── tests.py              # Test cases
        ├── migrations/           # Database migration files
        └── templates/            # HTML templates (13 files)
            ├── signup_page.html
            ├── login.html
            ├── dashboard.html
            ├── dashboard_option.html
            ├── facility_detail.html
            ├── complaints.html        # 🆕 Submit + my complaints
            ├── all_complaints.html    # 🆕 Secretary: manage all
            ├── notice_board.html      # 🆕 View notices
            ├── post_notice.html       # 🆕 Secretary: create notice
            ├── visitor_pass.html      # 🆕 Flat Owner: manage visitors
            ├── security_visitors.html # 🆕 Security: gate view
            ├── amenity_booking.html   # 🆕 Book + my bookings
            └── all_bookings.html      # 🆕 Secretary: all bookings
```

---

## 🚀 How to Run

### Prerequisites

- **Python 3.10+** installed on your system
- **pip** (comes with Python)

### Step-by-Step Setup

```bash
# 1. Clone or extract the project
#    (you should already have the "Ram College Project" folder)

# 2. Navigate to the project root
cd "Ram College Project/smartbuilding"

# 3. Create a virtual environment (skip if 'env' folder already exists)
python -m venv ../env

# 4. Activate the virtual environment
#    On Windows (PowerShell):
..\env\Scripts\Activate.ps1
#    On Windows (CMD):
..\env\Scripts\activate.bat
#    On macOS/Linux:
source ../env/bin/activate

# 5. Install dependencies
pip install -r requirements.txt

# 6. Apply database migrations
python manage.py migrate

# 7. Start the development server
python manage.py runserver
```

### Open in Browser

Once the server starts, open your browser and go to:

| Page | URL |
|------|-----|
| **Signup** | [http://127.0.0.1:8000/signup/](http://127.0.0.1:8000/signup/) |
| **Login** | [http://127.0.0.1:8000/login/](http://127.0.0.1:8000/login/) |
| **Dashboard** | [http://127.0.0.1:8000/dashboard/](http://127.0.0.1:8000/dashboard/) |
| **Complaints** | [http://127.0.0.1:8000/complaints/](http://127.0.0.1:8000/complaints/) |
| **Notice Board** | [http://127.0.0.1:8000/notices/](http://127.0.0.1:8000/notices/) |
| **Visitor Pass** | [http://127.0.0.1:8000/visitors/](http://127.0.0.1:8000/visitors/) |
| **Amenity Booking** | [http://127.0.0.1:8000/amenities/](http://127.0.0.1:8000/amenities/) |
| **Logout** | [http://127.0.0.1:8000/logout/](http://127.0.0.1:8000/logout/) |
| **Admin Panel** | [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) |

### Quick Start (First-Time User)

1. Go to `/signup/` → Register with a role, name, contact number, Aadhar, DOB, and password.
2. Go to `/login/` → Enter your contact number and password.
3. You'll be redirected to the **Dashboard** where you can explore all features.
4. Click your **profile icon** (top-right) to see profile details, upload a photo, or **logout**.

---

## 🔐 Authentication Flow

```
  ┌──────────┐       ┌──────────┐       ┌──────────────┐       ┌──────────┐
  │  Signup  │──────►│  Login   │──────►│  Dashboard   │──────►│  Logout  │
  │  Page    │       │  Page    │       │  (Protected) │       │  /logout │
  └──────────┘       └────┬─────┘       └──────┬───────┘       └────┬─────┘
                          │                     │                    │
                     Validates            Session check         Clears
                     contact +            (user_id in          session &
                     password             session?)            redirects
                          │                     │              to /login/
                          ▼                     ▼
                   ┌─────────────┐      ┌──────────────┐
                   │ check_      │      │ If no session │
                   │ password()  │      │ → redirect   │
                   │ (PBKDF2)    │      │   to /login/ │
                   └─────────────┘      └──────────────┘
```

- Passwords are **hashed** using Django's `make_password()` (PBKDF2 by default) — never stored in plain text.
- Sessions are stored server-side; only a session ID cookie is sent to the browser.
- Every protected view checks `request.session["user_id"]` before rendering.
- **Logout** calls `request.session.flush()` to destroy the session completely.

---

## 📦 Dependencies

Listed in `requirements.txt`:

| Package | Version | Purpose |
|---------|---------|---------|
| `Django` | 5.2.8 | Web framework |
| `asgiref` | 3.10.0 | ASGI utilities (Django dependency) |
| `Pillow` | 12.0.0 | Image processing for profile photo uploads |
| `sqlparse` | 0.5.3 | SQL formatting (Django dependency) |
| `tzdata` | 2025.2 | Timezone data for Windows |

---

## 📊 Database Models

| Model | Purpose | Key Fields |
|-------|---------|------------|
| **Signup** | User accounts | role, full_name, contact_number, aadhar_number, dob, password, profile_image |
| **Complaint** | Complaint tickets | ticket_number (auto TKT-XXXX), resident (FK), category, description, status, secretary_remarks |
| **Notice** | Announcements | title, content, category, is_urgent, posted_by (FK), is_active |
| **VisitorPass** | Visitor pre-approvals | flat_owner (FK), visitor_name, expected_date/time, status, flat_number, vehicle_number, marked_by (FK) |
| **AmenityBooking** | Facility bookings | amenity_name, booked_by (FK), booking_date, time_slot, purpose, num_guests, status |

---

## 🙋 FAQ

**Q: Can I use MySQL or PostgreSQL instead of SQLite?**
A: Yes. Update the `DATABASES` setting in `settings.py` with your database credentials. Django supports MySQL, PostgreSQL, Oracle, and more out of the box.

**Q: How do I create an admin/superuser?**
A: Run `python manage.py createsuperuser` and follow the prompts. Then access `/admin/`.

**Q: Is this production-ready?**
A: Not yet. For production you should: set `DEBUG = False`, use a proper web server (Gunicorn/Nginx), configure a production database, and set a strong `SECRET_KEY`.

**Q: How do I logout?**
A: Click your profile icon on the dashboard (top-right corner), then click the red **🚪 Logout** button at the bottom of the modal. Or go directly to `/logout/`.

---

## 📄 License

This project is developed for educational/academic purposes as part of a college project.

---

> Built with ❤️ using Django 5.2 — SmartBuilding Society Management System
