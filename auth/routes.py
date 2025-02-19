from flask import Blueprint, request, render_template, redirect, url_for, session
from flask import jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token
from database import get_db
from functools import wraps

bcrypt = Bcrypt()
auth_bp = Blueprint("auth", __name__, template_folder="templates")
dashboard_bp = Blueprint('dashboard', __name__)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        db = get_db()

        if db.users.find_one({"email": email}):
            return render_template("register.html", error="Email already registered")

        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
        db.users.insert_one({"email": email, "password": hashed_pw})
        return redirect(url_for('auth.login_page'))

    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        db = get_db()
        user = db.users.find_one({"email": email})

        if not user or not bcrypt.check_password_hash(user["password"], password):
            return render_template("login.html", error="Invalid credentials")

        access_token = create_access_token(identity=email)
        session['user'] = email
        session['token'] = access_token

        # ✅ Redirect to the dashboard after successful login
        return redirect(url_for('auth.dashboard'))

    return render_template("login.html")

@dashboard_bp.route('/job-description/submit', methods=['POST'])
def submit_job_description():
    data = request.get_json()
    job_description = data.get('job_description')

    if not job_description:
        return jsonify({"message": "Job description is required."}), 400

    # Example: Save to database or process as needed
    db = get_db()
    db.job_descriptions.insert_one({
        "user": session.get('user'),
        "description": job_description
    })

    return jsonify({"message": "Job description submitted successfully!"})

@auth_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=session.get('user'))

@auth_bp.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for('auth.login_page'))
