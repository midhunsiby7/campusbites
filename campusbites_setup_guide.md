# 🍽️ CampusBites — Team Setup Guide

> Follow these steps **exactly in order**. If you get stuck at any step, stop and ask before continuing.

---

## ✅ Prerequisites — Install These First

Before starting, make sure you have all of these installed:

| Tool | Download Link | Notes |
|---|---|---|
| **Python 3.12** | https://www.python.org/downloads/release/python-3120/ | During install, tick ✅ "Add Python to PATH" |
| **Git** | https://git-scm.com/download/win | Use default options |
| **MySQL Server 8.0** | https://dev.mysql.com/downloads/installer/ | Remember your `root` password! |
| **MySQL Workbench** *(optional)* | Comes with MySQL installer | Helpful to visually check the DB |
| **VS Code** *(recommended)* | https://code.visualstudio.com/ | For editing code |

> **Verify Python 3.12 is installed** — open PowerShell and run:
> ```powershell
> py -3.12 --version
> ```
> It should print `Python 3.12.x`

---

## 📁 Step 1 — Clone the Repository

Open **PowerShell** (search for it in Start Menu) and run:

```powershell
git clone https://github.com/midhunsiby7/campusbites.git
cd campusbites
```

You should now be inside the `campusbites` folder.

---

## 🐍 Step 2 — Create Virtual Environment (Python 3.12)

Still in PowerShell inside the `campusbites` folder, run:

```powershell
py -3.12 -m venv .venv
```

Then **activate** it:

```powershell
.\.venv\Scripts\Activate.ps1
```

> ✅ You'll know it worked when you see `(.venv)` at the start of your terminal line like:
> ```
> (.venv) PS D:\campusbites>
> ```

> ⚠️ **If you get an error about "execution policy"**, run this first, then try again:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

---

## 📦 Step 3 — Install Dependencies

With the venv activated, run:

```powershell
pip install -r requirements.txt
```

Wait for it to finish. It should end with `Successfully installed ...`

---

## 🗄️ Step 4 — Set Up the Database

### 4a. Create the database

Open **MySQL Workbench** or run in PowerShell:

```powershell
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p
```

Enter your MySQL root password. Then inside MySQL, run:

```sql
CREATE DATABASE campusbites;
EXIT;
```

### 4b. Run the schema to create all tables

Back in PowerShell (inside campusbites folder), run:

```powershell
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p campusbites < db\schema.sql
```

Enter your MySQL password when prompted.

> ✅ This creates all the tables automatically. You won't see any output — that means it worked.

---

## ⚙️ Step 5 — Create Your `.env` File

In PowerShell, run:

```powershell
copy .env.example .env
```

Now open `.env` in VS Code and fill in your values:

```powershell
code .env
```

Edit these fields:

```env
# Keep this exactly as is (or make up your own long string)
FLASK_SECRET_KEY=any_long_random_string_here

# Your MySQL password (whatever you set during MySQL installation)
DB_HOST=127.0.0.1
DB_USER=root
DB_PASSWORD=YOUR_MYSQL_PASSWORD_HERE
DB_NAME=campusbites
DB_PORT=3306

# Razorpay — ask Midhun for these values
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxx
RAZORPAY_KEY_SECRET=your_razorpay_secret
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret

# Firebase — ask Midhun for these values
FIREBASE_API_KEY=...
FIREBASE_AUTH_DOMAIN=...
FIREBASE_PROJECT_ID=...
FIREBASE_STORAGE_BUCKET=...
FIREBASE_MESSAGING_SENDER_ID=...
FIREBASE_APP_ID=...
FIREBASE_MEASUREMENT_ID=...

FIREBASE_CREDENTIALS_PATH=myserviceAccountKey.json
```

> ⚠️ **The only field you fill yourself** is `DB_PASSWORD`. Get all Firebase and Razorpay values from **Midhun**.

---

## 🔑 Step 6 — Add the Firebase Service Account Key

Midhun will share a file called `myserviceAccountKey.json` with you **privately** (via WhatsApp or email — NOT GitHub).

Place that file in the root of the project folder:

```
campusbites/
├── app.py
├── myserviceAccountKey.json   ← put it here
├── .env
└── ...
```

---

## 🚀 Step 7 — Run the App

Make sure your venv is still active (you should see `(.venv)` in the terminal). Then run:

```powershell
.\.venv\Scripts\python.exe app.py
```

> ✅ If successful, you'll see:
> ```
>  * Running on http://127.0.0.1:5055
> ```

Open your browser and go to: **http://127.0.0.1:5055**

---

## 🛠️ Common Errors & Fixes

| Error | Fix |
|---|---|
| `py -3.12 not found` | Install Python 3.12 from python.org and tick "Add to PATH" |
| `Activate.ps1 cannot be loaded` | Run `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| `No module named 'pkg_resources'` | Run `pip install "setuptools<72"` |
| `mysql is not recognized` | Use full path: `C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe` |
| `Access denied for user root` | Wrong MySQL password in `.env` |
| `Firebase: Error auth/api-key-not-valid` | Firebase values in `.env` are wrong — ask Midhun |
| `ModuleNotFoundError: No module named 'X'` | Run `pip install -r requirements.txt` again |

---

## 📞 Who to Ask for What

| Thing needed | Ask |
|---|---|
| Firebase config values | **Midhun** |
| `myserviceAccountKey.json` file | **Midhun** (via WhatsApp/email) |
| Razorpay keys | **Midhun** |
| MySQL password | Set your own during MySQL installation |

---

*Last updated: April 2026*
