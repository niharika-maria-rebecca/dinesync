from flask import Blueprint, render_template, request, redirect, url_for, abort, flash
from flask_login import login_required, current_user
from flask_bcrypt import Bcrypt
from functools import wraps
from models.dish import Dish
from models.user import User
from models import db

admin_bp = Blueprint('admin', __name__)
bcrypt   = Bcrypt()


# ── Admin only decorator ──
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated


# ── Dashboard ──
@admin_bp.route('/admin')
@login_required
@admin_required
def dashboard():
    dishes = Dish.query.order_by(Dish.category).all()
    staff  = User.query.filter(User.role != 'admin').all()
    return render_template('admin/dashboard.html',
                           dishes=dishes,
                           staff=staff)


# ── Add Dish ──
@admin_bp.route('/admin/add-dish', methods=['GET', 'POST'])
@login_required
@admin_required
def add_dish():
    if request.method == 'POST':
        dish = Dish(
            name              = request.form['name'],
            description       = request.form.get('description', ''),
            price             = float(request.form['price']),
            category          = request.form['category'],
            prep_time         = int(request.form.get('prep_time', 10)),
            is_available      = 'is_available'      in request.form,
            is_todays_special = 'is_todays_special' in request.form
        )
        db.session.add(dish)
        db.session.commit()
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/add_dish.html')


# ── Edit Dish ──
@admin_bp.route('/admin/edit-dish/<int:dish_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_dish(dish_id):
    dish = Dish.query.get_or_404(dish_id)
    if request.method == 'POST':
        dish.name              = request.form['name']
        dish.description       = request.form.get('description', '')
        dish.price             = float(request.form['price'])
        dish.category          = request.form['category']
        dish.prep_time         = int(request.form.get('prep_time', 10))
        dish.is_available      = 'is_available'      in request.form
        dish.is_todays_special = 'is_todays_special' in request.form
        db.session.commit()
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/edit_dish.html', dish=dish)


# ── Delete Dish ──
@admin_bp.route('/admin/delete-dish/<int:dish_id>', methods=['POST'])
@login_required
@admin_required
def delete_dish(dish_id):
    dish = Dish.query.get_or_404(dish_id)
    db.session.delete(dish)
    db.session.commit()
    return redirect(url_for('admin.dashboard'))


# ── Toggle Availability ──
@admin_bp.route('/admin/toggle-dish/<int:dish_id>', methods=['POST'])
@login_required
@admin_required
def toggle_dish(dish_id):
    dish             = Dish.query.get_or_404(dish_id)
    dish.is_available= not dish.is_available
    db.session.commit()
    return redirect(url_for('admin.dashboard'))


# ── Add Staff ──
@admin_bp.route('/admin/add-staff', methods=['GET', 'POST'])
@login_required
@admin_required
def add_staff():
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        role     = request.form.get('role', '').strip()

        # Check if email already exists
        existing = User.query.filter_by(email=email).first()
        if existing:
            dishes = Dish.query.order_by(Dish.category).all()
            staff  = User.query.filter(User.role != 'admin').all()
            return render_template('admin/dashboard.html',
                                   dishes=dishes,
                                   staff=staff,
                                   error='Email already exists!')

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        new_staff = User(
            name     = name,
            email    = email,
            password = hashed_pw,
            role     = role
        )
        db.session.add(new_staff)
        db.session.commit()
        return redirect(url_for('admin.dashboard'))

    return redirect(url_for('admin.dashboard'))


# ── Delete Staff ──
@admin_bp.route('/admin/delete-staff/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_staff(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin.dashboard'))


