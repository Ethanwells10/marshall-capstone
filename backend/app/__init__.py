from flask import Flask
from flask_cors import CORS
from .db import init_db, get_db
import os


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    CORS(app)

    # Initialize database
    init_db(app)

    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.watchlists import watchlists_bp
    from .routes.stocks import stocks_bp
    from .routes.notes import notes_bp
    from .routes.market import market_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(watchlists_bp, url_prefix="/api/watchlists")
    app.register_blueprint(stocks_bp, url_prefix="/api/stocks")
    app.register_blueprint(notes_bp, url_prefix="/api/notes")
    app.register_blueprint(market_bp, url_prefix="/api/market")

    @app.route("/")
    def index():
        return "<h1>Market Monitor</h1><p>API is running.</p>"

    @app.route("/api/health")
    def health():
        from datetime import datetime, timezone
        return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}

    @app.teardown_appcontext
    def close_db(exception):
        db = get_db()
        if db is not None:
            db.close()

    return app
