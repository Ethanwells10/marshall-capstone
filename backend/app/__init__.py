from flask import Flask, render_template, redirect, request
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
    from .routes.portfolio import portfolio_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(watchlists_bp, url_prefix="/api/watchlists")
    app.register_blueprint(stocks_bp, url_prefix="/api/stocks")
    app.register_blueprint(notes_bp, url_prefix="/api/notes")
    app.register_blueprint(market_bp, url_prefix="/api/market")
    app.register_blueprint(portfolio_bp, url_prefix="/api/portfolio")

    # Frontend page routes
    @app.route("/")
    def index():
        return render_template("about.html")

    @app.route("/login")
    def login_page():
        return render_template("login.html")

    @app.route("/dashboard")
    def dashboard_page():
        return render_template("dashboard.html")

    @app.route("/watchlists")
    def watchlists_page():
        return render_template("watchlists.html")

    @app.route("/notes")
    def notes_page():
        return render_template("notes.html")

    @app.route("/stock/<symbol>")
    def stock_page(symbol):
        return render_template("stock.html", symbol=symbol.upper())

    @app.route("/profile")
    def profile_page():
        return render_template("profile.html")

    @app.route("/browse")
    def browse_page():
        return render_template("browse.html")

    @app.route("/portfolio")
    def portfolio_page():
        return render_template("portfolio.html")

    @app.route("/search")
    def search_page():
        query = request.args.get("q", "").strip().upper()
        return render_template("search.html", query=query)

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
