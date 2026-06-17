import os
from flask import Flask, render_template
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO
from config import Config
from models import db
from models.user import User

login_manager = LoginManager()
bcrypt        = Bcrypt()
socketio      = SocketIO()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")

    login_manager.login_view = 'auth.login'

    from routes.auth     import auth_bp
    from routes.customer import customer_bp
    from routes.kitchen  import kitchen_bp
    from routes.admin    import admin_bp
    from routes.manager  import manager_bp
    from routes.chatbot  import chatbot_bp
    from routes.qr       import qr_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(kitchen_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(manager_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(qr_bp)

    with app.app_context():
        db.create_all()
        print("✅ Database tables created!")

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('403.html'), 404

    return app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))

    if os.environ.get('PORT') is None:
        import webbrowser, threading, time
        def open_browser():
            time.sleep(2)
            webbrowser.open(f'http://127.0.0.1:{port}')
        t = threading.Thread(target=open_browser)
        t.daemon = True
        t.start()

    socketio.run(app, debug=False, host='0.0.0.0', port=port)