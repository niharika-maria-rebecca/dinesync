from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from functools import wraps
from models.order import Order
from models.table import Table

manager_bp = Blueprint('manager', __name__)


def manager_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            from flask import redirect, url_for
            return redirect(url_for('auth.login'))
        if current_user.role not in ['manager', 'admin']:
            abort(403)
        return f(*args, **kwargs)
    return decorated


@manager_bp.route('/manager')
@login_required
@manager_required
def dashboard():
    orders = Order.query.order_by(Order.created_at.desc()).limit(50).all()
    tables = Table.query.all()

    total_revenue  = sum(o.total_amount for o in orders if o.status == 'served')
    active_orders  = Order.query.filter(Order.status.in_(['placed', 'preparing'])).count()
    served_today   = Order.query.filter_by(status='served').count()

    return render_template('manager/dashboard.html',
                           orders        = orders,
                           tables        = tables,
                           total_revenue = total_revenue,
                           active_orders = active_orders,
                           served_today  = served_today)