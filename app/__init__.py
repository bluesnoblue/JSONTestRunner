from flask import Flask
from flask_bootstrap import Bootstrap

bootstrap = Bootstrap()


def create_app():
    app = Flask(__name__)
    app.config.setdefault('BOOTSTRAP_SERVE_LOCAL', True)
    bootstrap.init_app(app)
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    return app
