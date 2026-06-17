from app import create_app
from models import db
from models.user import User
from models.table import Table
from flask_bcrypt import Bcrypt

app    = create_app()
bcrypt = Bcrypt(app)

with app.app_context():

    # Create Admin
    if not User.query.filter_by(role='admin').first():
        admin = User(
            name     = 'Super Admin',
            email    = 'admin@dinesync.com',
            password = bcrypt.generate_password_hash('Admin@123').decode('utf-8'),
            role     = 'admin'
        )
        db.session.add(admin)
        print("✅ Admin created — email: admin@dinesync.com | password: Admin@123")
    else:
        print("ℹ️  Admin already exists")

    # Create Kitchen Staff
    if not User.query.filter_by(email='kitchen@dinesync.com').first():
        kitchen = User(
            name     = 'Kitchen Staff',
            email    = 'kitchen@dinesync.com',
            password = bcrypt.generate_password_hash('Kitchen@123').decode('utf-8'),
            role     = 'kitchen'
        )
        db.session.add(kitchen)
        print("✅ Kitchen staff created — email: kitchen@dinesync.com | password: Kitchen@123")
    else:
        print("ℹ️  Kitchen staff already exists")

    # Create Manager
    if not User.query.filter_by(email='manager@dinesync.com').first():
        manager = User(
            name     = 'Restaurant Manager',
            email    = 'manager@dinesync.com',
            password = bcrypt.generate_password_hash('Manager@123').decode('utf-8'),
            role     = 'manager'
        )
        db.session.add(manager)
        print("✅ Manager created — email: manager@dinesync.com | password: Manager@123")
    else:
        print("ℹ️  Manager already exists")

    # Create Tables 1 to 10
    for i in range(1, 11):
        if not Table.query.filter_by(table_number=i).first():
            db.session.add(Table(table_number=i))
    print("✅ Tables 1–10 created")

    db.session.commit()
    print("\n🎉 Seed complete! You can now log in.")