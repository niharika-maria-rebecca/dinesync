from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from functools import wraps
from models.dish import Dish
from models.order import Order, OrderItem
from models.table import Table, CallWaiter
from models import db

customer_bp = Blueprint('customer', __name__)

def customer_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'customer':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@customer_bp.route('/table/<int:table_number>')
@customer_required
def menu(table_number):
    dishes     = Dish.query.all()
    specials   = Dish.query.filter_by(is_todays_special=True, is_available=True).all()
    categories = db.session.query(Dish.category).distinct().all()
    categories = [c[0] for c in categories]
    return render_template('customer/menu.html',
                           dishes=dishes,
                           specials=specials,
                           categories=categories,
                           table_number=table_number,
                           customer_name=session.get('customer_name', 'Guest'))

@customer_bp.route('/place-order', methods=['POST'])
@customer_required
def place_order():
    data          = request.get_json()
    table_number  = session.get('table_number', '1')
    customer_name = session.get('customer_name', 'Guest')
    table         = Table.query.filter_by(table_number=int(table_number)).first()
    if not table:
        return jsonify({'error': 'Table not found'}), 404
    order = Order(table_id=table.id, customer_name=customer_name, status='placed')
    db.session.add(order)
    db.session.flush()
    total = 0
    for item in data.get('items', []):
        dish = Dish.query.get(item['dish_id'])
        if dish and dish.is_available:
            oi = OrderItem(order_id=order.id, dish_id=dish.id,
                           quantity=item['quantity'], price_at_order=dish.price)
            total += dish.price * item['quantity']
            db.session.add(oi)
    order.total_amount = total
    db.session.commit()
    return jsonify({'success': True, 'order_id': order.id})

@customer_bp.route('/order-status/<int:order_id>')
@customer_required
def order_status(order_id):
    order = Order.query.get_or_404(order_id)
    return jsonify({'status': order.status})

# ── CALL WAITER ──
@customer_bp.route('/call-waiter', methods=['POST'])
@customer_required
def call_waiter():
    try:
        table_number  = session.get('table_number', '1')
        customer_name = session.get('customer_name', 'Guest')

        # Check if already called and not resolved
        existing = CallWaiter.query.filter_by(
            table_number=int(table_number),
            resolved=False
        ).first()

        if existing:
            return jsonify({
                'success': True,
                'message': 'Waiter already notified! They are on their way.'
            })

        call = CallWaiter(
            table_number  = int(table_number),
            customer_name = customer_name,
            resolved      = False
        )
        db.session.add(call)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Waiter notified for Table {table_number}! They will be there shortly.'
        })
    except Exception as e:
        print(f"Call waiter error: {e}")
        return jsonify({'success': False, 'message': 'Could not notify waiter. Please try again.'})