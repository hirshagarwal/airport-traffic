from flask import Flask

from config import load_config


def create_app() -> Flask:
    """Application factory for the airport traffic estimator."""
    app = Flask(__name__)

    # Load shared configuration (API keys, etc.) into the Flask config mapping.
    app.config["APP_CONFIG"] = load_config()

    from .routes import bp as main_bp

    app.register_blueprint(main_bp)

    return app
