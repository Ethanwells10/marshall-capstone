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
                db.execute("INSERT OR IGNORE INTO watchlists (user_id, name) VALUES (?, 'Healthcare & Energy')", (admin_id,))

                tech_wl = db.execute("SELECT id FROM watchlists WHERE user_id = ? AND name = 'Tech Stocks'", (admin_id,)).fetchone()
                fin_wl = db.execute("SELECT id FROM watchlists WHERE user_id = ? AND name = 'Finance'", (admin_id,)).fetchone()
                health_wl = db.execute("SELECT id FROM watchlists WHERE user_id = ? AND name = 'Healthcare & Energy'", (admin_id,)).fetchone()

                if tech_wl:
                    for sym in ["AAPL", "MSFT", "GOOGL", "NVDA", "META", "AMZN"]:
                        db.execute("INSERT OR IGNORE INTO watchlist_items (watchlist_id, ticker_symbol) VALUES (?, ?)", (tech_wl[0], sym))

                if fin_wl:
                    for sym in ["JPM", "V", "GS", "BAC"]:
                        db.execute("INSERT OR IGNORE INTO watchlist_items (watchlist_id, ticker_symbol) VALUES (?, ?)", (fin_wl[0], sym))

                if health_wl:
                    for sym in ["JNJ", "UNH", "XOM"]:
                        db.execute("INSERT OR IGNORE INTO watchlist_items (watchlist_id, ticker_symbol) VALUES (?, ?)", (health_wl[0], sym))

                # Sample notes
                db.execute("INSERT OR IGNORE INTO user_notes (user_id, ticker_symbol, note_text) VALUES (?, 'AAPL', 'Strong services revenue growth. Watch for iPhone sales in Q2.')", (admin_id,))
                db.execute("INSERT OR IGNORE INTO user_notes (user_id, ticker_symbol, note_text) VALUES (?, 'NVDA', 'AI chip demand remains high. Data center revenue is key metric.')", (admin_id,))
                db.execute("INSERT OR IGNORE INTO user_notes (user_id, ticker_symbol, note_text) VALUES (?, 'TSLA', 'Delivery numbers coming soon. Cybertruck ramp-up is a wildcard.')", (admin_id,))
                db.execute("INSERT OR IGNORE INTO user_notes (user_id, ticker_symbol, note_text) VALUES (?, 'MSFT', 'Azure growth steady. Copilot monetization is the next catalyst.')", (admin_id,))
                db.execute("INSERT OR IGNORE INTO user_notes (user_id, ticker_symbol, note_text) VALUES (?, 'JPM', 'Interest rate environment favorable. Watch credit card delinquency trends.')", (admin_id,))
                db.execute("INSERT OR IGNORE INTO user_notes (user_id, ticker_symbol, note_text) VALUES (?, 'GOOGL', 'Search ad revenue still dominant. Cloud segment approaching profitability.')", (admin_id,))

                # Pre-seed API cache with sample market data so dashboard always has content
                import json
                from datetime import datetime, timedelta, timezone

                sample_quotes = {
                    "AAPL": {"price": 270.23, "change": 3.45, "change_percent": 1.29, "volume": 54320100},
                    "MSFT": {"price": 448.12, "change": -2.10, "change_percent": -0.47, "volume": 21450000},
                    "GOOGL": {"price": 176.88, "change": 1.92, "change_percent": 1.10, "volume": 18900000},
                    "NVDA": {"price": 950.02, "change": 15.30, "change_percent": 1.64, "volume": 42100000},
                    "META": {"price": 595.40, "change": -4.20, "change_percent": -0.70, "volume": 15200000},
                    "AMZN": {"price": 198.75, "change": 2.80, "change_percent": 1.43, "volume": 31800000},
                    "TSLA": {"price": 245.60, "change": -8.40, "change_percent": -3.31, "volume": 68500000},
                    "JPM": {"price": 212.50, "change": 1.15, "change_percent": 0.54, "volume": 8900000},
                    "V": {"price": 315.20, "change": 0.85, "change_percent": 0.27, "volume": 6200000},
                    "JNJ": {"price": 158.90, "change": -0.45, "change_percent": -0.28, "volume": 7100000},
                    "SPY": {"price": 562.80, "change": 4.20, "change_percent": 0.75, "volume": 72000000},
                    "QQQ": {"price": 487.35, "change": 5.60, "change_percent": 1.16, "volume": 38000000},
                    "DIA": {"price": 425.10, "change": 2.80, "change_percent": 0.66, "volume": 3200000},
                    "GS": {"price": 498.30, "change": 3.20, "change_percent": 0.65, "volume": 2100000},
                    "BAC": {"price": 42.15, "change": 0.35, "change_percent": 0.84, "volume": 28000000},
                    "UNH": {"price": 528.40, "change": -2.60, "change_percent": -0.49, "volume": 3400000},
                    "XOM": {"price": 112.85, "change": 1.50, "change_percent": 1.35, "volume": 12500000},
                    "DIS": {"price": 112.20, "change": 0.90, "change_percent": 0.81, "volume": 9800000},
                }

                cache_expiry = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
                for sym, quote in sample_quotes.items():
                    cache_key = f"alphavantage:quote:{sym}"
                    db.execute("""
                        INSERT OR IGNORE INTO api_cache (cache_key, cache_data, expires_at)
                        VALUES (?, ?, ?)
                    """, (cache_key, json.dumps(quote), cache_expiry))

                # Seed sample price history for charts
                import random
                random.seed(42)
                history_expiry = (datetime.now(timezone.utc) + timedelta(hours=48)).isoformat()

                base_prices = {
                    "AAPL": 250, "MSFT": 420, "GOOGL": 165, "NVDA": 880, "META": 570,
                    "AMZN": 185, "TSLA": 260, "JPM": 200, "V": 305, "JNJ": 155,
                    "SPY": 545, "QQQ": 470, "DIA": 415, "GS": 480, "BAC": 40,
                    "UNH": 520, "XOM": 108, "DIS": 108
                }

                for sym, base in base_prices.items():
                    # Generate 22 days of data (1M)
                    prices_1m = []
                    price = base
                    for d in range(22):
                        price = round(price * (1 + random.uniform(-0.025, 0.03)), 2)
                        date = (datetime.now() - timedelta(days=22-d)).strftime("%Y-%m-%d")
                        prices_1m.append({"date": date, "close": price})

                    cache_key = f"alphavantage:history:{sym}:1M"
                    db.execute("""
                        INSERT OR IGNORE INTO api_cache (cache_key, cache_data, expires_at)
                        VALUES (?, ?, ?)
                    """, (cache_key, json.dumps(prices_1m), history_expiry))

                    # 1W = last 5 days from the 1M data
                    cache_key = f"alphavantage:history:{sym}:1W"
                    db.execute("""
                        INSERT OR IGNORE INTO api_cache (cache_key, cache_data, expires_at)
                        VALUES (?, ?, ?)
                    """, (cache_key, json.dumps(prices_1m[-5:]), history_expiry))

                # Sample portfolio transactions
                portfolio_data = [
                    (admin_id, 'AAPL', 'buy', 15, 178.50, '2025-09-15', 'Initial position'),
                    (admin_id, 'AAPL', 'buy', 10, 185.20, '2025-11-20', 'Added on dip'),
                    (admin_id, 'MSFT', 'buy', 12, 415.00, '2025-10-01', 'Cloud growth thesis'),
                    (admin_id, 'NVDA', 'buy', 8, 520.75, '2025-08-10', 'AI play'),
                    (admin_id, 'NVDA', 'buy', 5, 480.00, '2025-12-05', 'Averaged down'),
                    (admin_id, 'GOOGL', 'buy', 20, 165.30, '2025-10-15', 'Undervalued vs peers'),
                    (admin_id, 'JPM', 'buy', 10, 198.40, '2025-11-01', 'Rate environment play'),
                    (admin_id, 'AMZN', 'buy', 8, 195.60, '2026-01-10', 'AWS momentum'),
                ]
                for tx in portfolio_data:
                    db.execute("""
                        INSERT OR IGNORE INTO portfolio_transactions
                        (user_id, ticker_symbol, transaction_type, shares, price_per_share, transaction_date, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, tx)

        db.commit()
        db.close()
