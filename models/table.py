from models import db
from datetime import datetime

class Table(db.Model):
    __tablename__  = 'tables'
    id             = db.Column(db.Integer, primary_key=True)
    table_number   = db.Column(db.Integer, unique=True, nullable=False)
    status         = db.Column(db.String(20), default='free')
    customer_name  = db.Column(db.String(100), nullable=True)

class CallWaiter(db.Model):
    __tablename__  = 'call_waiter'
    id             = db.Column(db.Integer, primary_key=True)
    table_number   = db.Column(db.Integer, nullable=False)
    customer_name  = db.Column(db.String(100), nullable=True)
    called_at      = db.Column(db.DateTime, default=datetime.utcnow)
    resolved       = db.Column(db.Boolean, default=False)