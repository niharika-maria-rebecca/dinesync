from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_login import login_user, logout_user
from flask_bcrypt import Bcrypt
from models.user import User
from models.table import Table
from models import db

auth_bp = Blueprint('auth', __name__)
bcrypt  = Bcrypt()

@auth_bp.route('/')
def home():
    return render_template('index.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        table = request.args.get('table', '1')
        return render_template('login.html', table=table)

    # ── DEBUG: print everything received from form ──
    print("=== LOGIN FORM DATA ===")
    print("Form data:", dict(request.form))
    print("Role received:", request.form.get('role'))
    print("Name received:", request.form.get('customer_name'))
    print("Table received:", request.form.get('table_number'))
    print("=======================")

    role = request.form.get('role', '').strip()

    if role == 'customer':
        name         = request.form.get('customer_name', '').strip()
        table_number = request.form.get('table_number', '1').strip()

        print(f"Customer login: name={name}, table={table_number}")

        if not name:
            print("ERROR: No name entered")
            return render_template('login.html',
                                   error='Please enter your name.',
                                   table=table_number)

        session['customer_name'] = name
        session['table_number']  = table_number
        session['role']          = 'customer'

        print(f"Session set: {dict(session)}")

        try:
            table_num = int(table_number)
            table_obj = Table.query.filter_by(table_number=table_num).first()
            if table_obj:
                table_obj.status        = 'occupied'
                table_obj.customer_name = name
                db.session.commit()
                print(f"Table {table_num} marked occupied")
            else:
                print(f"WARNING: Table {table_num} not found in DB")
        except Exception as e:
            print(f"Table error: {e}")

        redirect_url = url_for('customer.menu', table_number=int(table_number))
        print(f"Redirecting to: {redirect_url}")
        return redirect(redirect_url)

    # ── STAFF ──
    email    = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()

    print(f"Staff login: email={email}, role={role}")

    if not email or not password:
        return render_template('login.html',
                               error='Please enter email and password.')

    user = User.query.filter_by(email=email, role=role).first()

    if user and bcrypt.check_password_hash(user.password, password):
        login_user(user)
        session['role'] = role
        print(f"Staff login success: {role}")

        if role == 'kitchen': return redirect(url_for('kitchen.queue'))
        if role == 'manager': return redirect(url_for('manager.dashboard'))
        if role == 'admin':   return redirect(url_for('admin.dashboard'))
    else:
        print("Staff login failed: wrong credentials")
        return render_template('login.html',
                               error='Invalid email or password.')


@auth_bp.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('auth.home'))