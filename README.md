# 🍔 CampusBites

> A smart canteen order management system built for college campuses.

CampusBites lets students browse today's menu, add items to cart, pay online via Razorpay, and receive a unique token number to collect their food — all from their phone. Canteen admins manage menu, stock, orders, and walk-in sales from a dedicated dashboard.

## ✨ Features

### Student App
- 🔐 Firebase Authentication (Google Login + Email/Password)
- 🍕 Browse daily menu with live stock updates
- 🛒 Add to cart & checkout with Razorpay payments
- 🎫 Unique token number per order for collection
- 📜 Order history and QR code for verification
- ⚙️ Profile settings with dark/light theme toggle

### Admin Dashboard
- 📊 Live order feed with status management (Confirm / Deliver)
- 🍽️ Menu management — add, edit, delete food items
- 📅 Today's Menu with per-day scheduling and stock control
- 🎫 Offline token generation for walk-in cash orders
- 📷 QR code scanner for order verification
- 📋 Uncollected token tracking

### System
- ⏰ Automated daily cleanup & menu reset (configurable via `.env`)
- 🔒 CSRF protection on all POST endpoints
- 🚦 Rate limiting to prevent abuse
- 🖼️ Auto image optimization (WebP conversion, smart resizing)

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, Flask |
| Database | MySQL 8.0 |
| Authentication | Firebase Admin SDK |
| Payments | Razorpay (Test/Live) |
| Frontend | HTML5, CSS3, JavaScript |
| Deployment | Gunicorn, Railway |

## 📁 Project Structure

```
CAMPUSBITES/
├── app.py                  # Main Flask application
├── hash_admin_password.py  # Admin password management utility
├── requirements.txt        # Python dependencies
├── Procfile                # Railway/Render deployment config
├── .env.example            # Environment variables template
├── db/
│   └── schema.sql          # Database schema
├── static/
│   ├── css/                # Stylesheets (style.css, admin.css, etc.)
│   ├── js/                 # Client-side JavaScript (theme.js)
│   ├── images/             # Static assets (logo, login background)
│   └── uploads/            # User-uploaded food images
└── templates/              # Jinja2 HTML templates
    ├── intro.html          # Splash / landing page
    ├── login.html          # Glassmorphism animated login
    ├── index.html          # Student home page (menu grid)
    ├── food_detail.html    # Food item detail + order
    ├── cart.html           # Shopping cart + checkout
    ├── orders.html         # Order history
    ├── settings.html       # User profile settings
    ├── admin_login.html    # Admin authentication
    ├── admin_dashboard.html# Order management dashboard
    ├── admin_foods.html    # Food item CRUD
    ├── todays_menu.html    # Daily menu manager
    └── scan_qr.html        # QR verification scanner
```

## 🚀 Setup

### Prerequisites
- Python 3.10+
- MySQL 8.0+
- Firebase project (for authentication)
- Razorpay account (for payments)

### Installation

1. **Clone the repo**
   ```bash
   git clone https://github.com/midhunsiby7/campusbites.git
   cd campusbites
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate    # Windows
   source .venv/bin/activate  # Mac/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**
   ```bash
   mysql -u root -p < db/schema.sql
   ```

5. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

6. **Set up Firebase**
   - Download your Firebase service account key
   - Save it as `myserviceAccountKey.json` in the project root

7. **Create an admin user**
   ```bash
   python hash_admin_password.py
   ```

8. **Run the server**
   ```bash
   python app.py
   ```
   Visit `http://localhost:5055`

## ⚙️ Environment Variables

See [`.env.example`](.env.example) for the full list. Key variables:

| Variable | Description |
|----------|-------------|
| `FLASK_SECRET_KEY` | Secret key for session security |
| `DB_HOST` / `DB_USER` / `DB_PASSWORD` / `DB_NAME` | MySQL connection |
| `RAZORPAY_KEY_ID` / `RAZORPAY_KEY_SECRET` | Payment gateway |
| `FIREBASE_API_KEY` / `FIREBASE_PROJECT_ID` | Firebase auth config |
| `CLEANUP_TIME` | Daily order archival time (HH:MM, IST) |
| `MENU_AUTOSET_TIME` | Daily menu auto-populate time (HH:MM, IST) |

## 🚂 Railway Deployment

1. Push code to GitHub
2. Connect your Railway project to the GitHub repo
3. Add all environment variables from `.env.example` in Railway dashboard
4. Add a MySQL plugin in Railway for the database
5. Railway auto-detects the `Procfile` and deploys

## 👨‍💻 Team

- **Midhun Siby**
- **Keerthana S Nair**
- **Keerthana V Saji**

## 📄 License

This project is for educational purposes.
