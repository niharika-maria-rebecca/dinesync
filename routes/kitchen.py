from flask import Blueprint, render_template, request, jsonify, abort
from flask_login import login_required, current_user
from functools import wraps
from models.order import Order
from models.table import CallWaiter
from models import db

kitchen_bp = Blueprint('kitchen', __name__)

def kitchen_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'kitchen':
            abort(403)
        return f(*args, **kwargs)
    return decorated

@kitchen_bp.route('/kitchen')
@login_required
@kitchen_required
def queue():
    # FCFS — oldest order first
    orders = Order.query.filter(
        Order.status.in_(['placed', 'preparing', 'ready'])
    ).order_by(Order.created_at.asc()).all()

    # Unresolved waiter calls
    waiter_calls = CallWaiter.query.filter_by(resolved=False).order_by(CallWaiter.called_at.asc()).all()

    return render_template('kitchen/queue.html',
                           orders=orders,
                           waiter_calls=waiter_calls)

@kitchen_bp.route('/kitchen/update-status', methods=['POST'])
@login_required
@kitchen_required
def update_status():
    data     = request.get_json()
    order    = Order.query.get_or_404(data.get('order_id'))
    order.status = data.get('status')
    db.session.commit()
    return jsonify({'success': True, 'order_id': order.id, 'status': order.status})

@kitchen_bp.route('/kitchen/resolve-waiter/<int:call_id>', methods=['POST'])
@login_required
@kitchen_required
def resolve_waiter(call_id):
    call = CallWaiter.query.get_or_404(call_id)
    call.resolved = True
    db.session.commit()
    return jsonify({'success': True})
@kitchen_bp.route('/kitchen/waiter-calls')
@login_required
@kitchen_required
def waiter_calls():
    from models.table import CallWaiter
    calls = CallWaiter.query.filter_by(resolved=False).order_by(CallWaiter.called_at.asc()).all()
    return jsonify({
        'calls': [{
            'id':            c.id,
            'table_number':  c.table_number,
            'customer_name': c.customer_name,
            'called_at':     c.called_at.strftime('%H:%M:%S')
        } for c in calls]
    })