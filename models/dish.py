from models import db

class Dish(db.Model):
    __tablename__     = 'dishes'
    id                = db.Column(db.Integer, primary_key=True)
    name              = db.Column(db.String(150), nullable=False)
    description       = db.Column(db.String(300), default='')
    price             = db.Column(db.Float, nullable=False)
    category          = db.Column(db.String(50), nullable=False)
    image             = db.Column(db.String(200), default='')
    is_available      = db.Column(db.Boolean, default=True)
    prep_time         = db.Column(db.Integer, default=10)
    is_todays_special = db.Column(db.Boolean, default=False)