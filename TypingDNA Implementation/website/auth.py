from flask import Blueprint, render_template, make_response, request, flash, jsonify, redirect, url_for, session, send_file
from flask_login import login_user, login_required, logout_user, current_user
from . import db
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
import re
import pyotp
import qrcode
from io import BytesIO

auth = Blueprint('auth', __name__)

@auth.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if user:
        if not check_password_hash(user.password, password):
            return make_response(jsonify({'message': 'Password incorrect.'}), 401)

        login_user(user, remember=True)  # Log in the user
        return make_response(jsonify({'message': 'Login successful', 'user_id': user.typing_id}), 200)
    else:
        return make_response(jsonify({'message': 'No user with that email.'}), 401)

# Function to validate email format
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

@auth.route("/api/sign-up", methods=["POST"])
def api_sign_up():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    user = User.query.filter_by(email=email).first()

    if not email or not is_valid_email(email):
        return make_response(jsonify({"message": "Email format is invalid!"}), 401)
    elif user:
        return make_response(jsonify({"message": "Email is already registered!"}), 401)
    elif not password or len(password) < 7:
        return make_response(jsonify({"message": "Password is too short!"}), 401)
    else:
        new_user = User(email=email, password=generate_password_hash(password, method="pbkdf2:sha512"))
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)  # Log in the new user
        return make_response(jsonify({"message": "User Created!", "user_id": new_user.typing_id}), 201)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.secret_key:
                return redirect(url_for('auth.verify_otp'))
            else:
                return redirect(url_for('main.profile'))
        else:
            flash('Login failed. Check your credentials.', 'danger')
            return redirect(url_for('auth.login'))
    return render_template('login.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if not email or not is_valid_email(email):
            flash('Email format is invalid!', category='error')
        elif user:
            flash('Email is already registered!', category='error')
        elif not password or len(password) < 7:
            flash('Password is too short!', category='error')
        else:
            new_user = User(email=email, password=generate_password_hash(password, method='pbkdf2:sha512'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.upload_file'))

    return render_template("sign_up.html")

@auth.route('/setup_2fa')
@login_required
def setup_2fa():
    user = User.query.get(current_user.id)
    if not user.secret_key:
        user.secret_key = pyotp.random_base32()
        db.session.commit()

    totp = pyotp.TOTP(user.secret_key)
    uri = totp.provisioning_uri(user.email, issuer_name="YourApp")
    qr = qrcode.make(uri)
    qr_io = BytesIO()
    qr.save(qr_io, 'PNG')
    qr_io.seek(0)

    return send_file(qr_io, mimetype='image/png')

@auth.route('/verify_otp', methods=['GET', 'POST'])
@login_required
def verify_otp():
    if request.method == 'POST':
        otp = request.form['otp']
        user = User.query.get(current_user.id)

        totp = pyotp.TOTP(user.secret_key)
        if totp.verify(otp):
            # OTP is valid
            flash('2FA setup complete.', 'success')
            return redirect(url_for('main.profile'))
        else:
            # OTP is invalid
            flash('Invalid OTP. Please try again.', 'danger')
            return redirect(url_for('auth.verify_otp'))
    return render_template('verify_otp.html')