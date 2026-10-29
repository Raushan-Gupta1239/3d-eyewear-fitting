# 3D Eyewear Fitting - Authentication Service

A secure, modern authentication module built with **Flask**, **MongoDB Atlas**, and **Google OAuth 2.0**. This service provides user management, credential encryption, and single sign-on (SSO) integration for the 3D Eyewear Fitting platform.

---

## Features

- **MongoDB Atlas Integration**: Cloud database connectivity using `pymongo` with automatic schema indexing and duplicate username prevention.
- **Google OAuth 2.0 (SSO)**: One-click "Continue with Google" sign-in via OpenID Connect powered by `authlib`.
- **Traditional Authentication**: Username and password registration and login with secure password hashing (`werkzeug.security`).
- **Session Management**: Secure, cookie-based session handling with protected homepage routes and instant logout.
- **Modern Responsive UI**: Clean, responsive styling with official Google sign-in branding.

---

## Tech Stack

- **Backend**: Python 3.13, Flask 3.1
- **Database**: MongoDB Atlas (Cloud NoSQL)
- **Authentication**: Authlib (OAuth 2.0 & OpenID Connect), Werkzeug Security
- **Configuration**: `python-dotenv`

---

## Project Structure

```text
MY WORK/
├── app.py                # Main Flask application & authentication routes
├── requirements.txt      # Project dependencies
├── .env                  # Local secret keys & database URI (git-ignored)
├── .env.example          # Environment variable template
├── .gitignore            # Git exclusion rules
├── static/
│   └── style.css         # Custom responsive styles & Google button UI
└── templates/
    ├── login.html        # Login page with standard & Google sign-in
    ├── register.html     # Registration page
    └── home.html         # Protected home page for authenticated users
```

---

## Getting Started

### 1. Prerequisites

- Python 3.10+ installed
- A [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) account and cluster
- A [Google Cloud Console](https://console.cloud.google.com/) project with OAuth 2.0 credentials

### 2. Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/Raushan-Gupta1239/3d-eyewear-fitting.git
cd 3d-eyewear-fitting
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the root directory by copying the example:

```bash
cp .env.example .env
```

Fill in your actual credentials in `.env`:

```env
# MongoDB Atlas Connection URI
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.vjgzcgp.mongodb.net/flask_db?retryWrites=true&w=majority

# Flask Session Secret
SECRET_KEY=your_random_secret_key

# Google OAuth Credentials
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret
```

> **Note**: In your Google Cloud Console OAuth Client settings, make sure the authorized redirect URI includes:
> - `http://localhost:5000/login/google/callback`
> - `http://127.0.0.1:5000/login/google/callback`

### 4. Running the Application

Start the Flask development server:

```bash
python app.py
```

Open your browser and navigate to:
```
http://localhost:5000
```

---

## API Endpoints & Routes

| Route | Method | Description |
| :--- | :--- | :--- |
| `/` | `GET` | Protected homepage (requires login) |
| `/login` | `GET`, `POST` | User login with username and password |
| `/register` | `GET`, `POST` | Create a new user account |
| `/login/google` | `GET` | Redirects user to Google OAuth consent screen |
| `/login/google/callback` | `GET` | Handles Google OAuth response and establishes session |
| `/logout` | `GET` | Clears active session and redirects to login |

---

## Security Best Practices

- All passwords are encrypted with `generate_password_hash` using salted SHA-256 before storing.
- Secrets, database URIs, and OAuth client keys are stored exclusively in `.env` and kept out of version control via `.gitignore`.
