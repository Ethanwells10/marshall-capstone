import sqlite3
import os
from flask import g

DATABASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "market_monitor.db")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def init_db(app):
    with app.app_context():
        db = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")

        # Read and execute schema
        schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "schema.sql")
        with open(schema_path, "r") as f:
            db.executescript(f.read())

        # Check if sample data needs to be loaded
        cursor = db.execute("SELECT COUNT(*) FROM tickers")
        count = cursor.fetchone()[0]
        if count == 0:
            sample_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_data.sql")
            if os.path.exists(sample_path):
                # We need to handle the admin password hash here
                from werkzeug.security import generate_password_hash
                admin_hash = generate_password_hash("admin123")

                with open(sample_path, "r") as f:
                    sql = f.read().replace("PLACEHOLDER_HASH", admin_hash)
                db.executescript(sql)

            # Also create sample watchlists for the admin user
            admin = db.execute("SELECT id FROM users WHERE email = 'admin@marketmonitor.com'").fetchone()
            if admin:
                admin_id = admin[0]
                db.execute("INSERT OR IGNORE INTO watchlists (user_id, name) VALUES (?, 'Tech Stocks')", (admin_id,))
                db.execute("INSERT OR IGNORE INTO watchlists (user_id, name) VALUES (?, 'Finance')", (admin_id,))

                tech_wl = db.execute("SELECT id FROM watchlists WHERE user_id = ? AND name = 'Tech Stocks'", (admin_id,)).fetchone()
                fin_wl = db.execute("SELECT id FROM watchlists WHERE user_id = ? AND name = 'Finance'", (admin_id,)).fetchone()

                if tech_wl:
                    for sym in ["AAPL", "MSFT", "GOOGL", "NVDA", "META"]:
                        db.execute("INSERT OR IGNORE INTO watchlist_items (watchlist_id, ticker_symbol) VALUES (?, ?)", (tech_wl[0], sym))

                if fin_wl:
                    for sym in ["JPM", "V"]:
                        db.execute("INSERT OR IGNORE INTO watchlist_items (watchlist_id, ticker_symbol) VALUES (?, ?)", (fin_wl[0], sym))

                # Sample notes
                db.execute("INSERT OR IGNORE INTO user_notes (user_id, ticker_symbol, note_text) VALUES (?, 'AAPL', 'Strong services revenue growth. Watch for iPhone sales in Q2.')", (admin_id,))
                db.execute("INSERT OR IGNORE INTO user_notes (user_id, ticker_symbol, note_text) VALUES (?, 'NVDA', 'AI chip demand remains high. Data center revenue is key metric.')", (admin_id,))

        db.commit()
        db.close()
