from models import db
from datetime import datetime

class Order(db.Model):
    __tablename__  = 'orders'
    id             = db.Column(db.Integer, primary_key=True)
    table_id       = db.Column(db.Integer, db.ForeignKey('tables.id'))
    customer_name  = db.Column(db.String(100), nullable=False)
    status         = db.Column(db.String(20), default='placed')
    total_amount   = db.Column(db.Float, default=0.0)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
    items          = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    __tablename__  = 'order_items'
    id             = db.Column(db.Integer, primary_key=True)
    order_id       = db.Column(db.Integer, db.ForeignKey('orders.id'))
    dish_id        = db.Column(db.Integer, db.ForeignKey('dishes.id'))
    quantity       = db.Column(db.Integer, default=1)
    price_at_order = db.Column(db.Float, nullable=False)
    dish           = db.relationship('Dish', backref='order_items')