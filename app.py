import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from authlib.integrations.flask_client import OAuth

# Allow HTTP for local OAuth development
os.environ["AUTHLIB_INSECURE_TRANSPORT"] = "1"

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change-this-to-a-random-secret-key")

# Database connection
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI is not set in environment variables or .env file.")

client = MongoClient(MONGO_URI)
try:
    db = client.get_default_database()
except Exception:
    db = client["flask_db"]

if db is None:
    db = client["flask_db"]

users_collection = db["users"]


# OAuth Setup
oauth = OAuth(app)
oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


# Create indexes
def init_db():
    try:
        users_collection.create_index("username", unique=True)
        print("Connected to MongoDB Atlas and verified unique index on 'username'.")
    except Exception as e:
        print(f"Warning: Could not connect to MongoDB or initialize index: {e}")


# Registration page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("All fields are required.")
            return redirect(url_for("register"))

        try:
            hashed_password = generate_password_hash(password)

            users_collection.insert_one({
                "username": username,
                "password": hashed_password,
                "auth_provider": "local"
            })

            flash("Registration successful! Please log in.")
            return redirect(url_for("login"))

        except DuplicateKeyError:
            flash("Username already exists.")
        except Exception as e:
            flash(f"Database error: {e}")

    return render_template("register.html")


# Login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        try:
            user = users_collection.find_one({"username": username})

            if user and not user.get("password") and user.get("auth_provider") == "google":
                flash("This account was created with Google. Please click 'Continue with Google' to sign in.")
                return render_template("login.html")

            if user and user.get("password") and check_password_hash(user["password"], password):
                session.clear()
                session["user_id"] = str(user["_id"])
                session["username"] = user["username"]

                return redirect(url_for("home"))

            flash("Invalid username or password.")
        except Exception as e:
            flash(f"Database error: {e}")

    return render_template("login.html")


# Google OAuth - Initiate login
@app.route("/login/google")
def google_login():
    google_id = os.getenv("GOOGLE_CLIENT_ID", "")
    google_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")

    if (
        not google_id
        or not google_secret
        or "your_google_client_id" in google_id
        or "your_google_client_secret" in google_secret
    ):
        flash("Google OAuth is not configured yet. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env.")
        return redirect(url_for("login"))

    redirect_uri = url_for("google_callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


# Google OAuth - Callback
@app.route("/login/google/callback")
def google_callback():
    try:
        token = oauth.google.authorize_access_token()
        user_info = token.get("userinfo")
        if not user_info:
            resp = oauth.google.get("https://openidconnect.googleapis.com/v1/userinfo", token=token)
            user_info = resp.json()
    except Exception as e:
        flash(f"Google login failed: {e}")
        return redirect(url_for("login"))

    email = user_info.get("email")
    google_id = user_info.get("sub")
    name = user_info.get("name") or (email.split("@")[0] if email else "Google User")

    if not email:
        flash("Could not retrieve email from Google.")
        return redirect(url_for("login"))

    try:
        # Check if user already exists
        user = users_collection.find_one({
            "$or": [
                {"google_id": google_id},
                {"email": email},
                {"username": email}
            ]
        })

        if user:
            user_id = str(user["_id"])
            username = user.get("username", email)
            # Update google_id and email if not linked
            if not user.get("google_id"):
                users_collection.update_one(
                    {"_id": user["_id"]},
                    {"$set": {"google_id": google_id, "email": email, "auth_provider": "google"}}
                )
        else:
            # Create a unique username for the user
            chosen_username = email
            if users_collection.find_one({"username": chosen_username}):
                chosen_username = f"{email.split('@')[0]}_{google_id[:5]}"

            result = users_collection.insert_one({
                "username": chosen_username,
                "email": email,
                "name": name,
                "google_id": google_id,
                "auth_provider": "google"
            })
            user_id = str(result.inserted_id)
            username = chosen_username

        session.clear()
        session["user_id"] = user_id
        session["username"] = username

        return redirect(url_for("home"))

    except Exception as e:
        flash(f"Database error during Google login: {e}")
        return redirect(url_for("login"))


# Homepage (login required)
@app.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("home.html")


# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
