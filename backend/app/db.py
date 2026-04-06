import pymysql
import pymysql.cursors
import os
from flask import g


def get_db_config():
    return {
        "host": os.environ.get("MYSQL_HOST", "localhost"),
        "user": os.environ.get("MYSQL_USER", "market_user"),
        "password": os.environ.get("MYSQL_PASSWORD", "market_pass"),
        "database": os.environ.get("MYSQL_DATABASE", "market_monitor"),
        "charset": "utf8mb4",
        "cursorclass": pymysql.cursors.DictCursor,
    }


class DBWrapper:
    """Wraps a PyMySQL connection to provide a sqlite3-like interface."""

    def __init__(self, conn):
        self.conn = conn

    def execute(self, query, params=None):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()


def get_db():
    if "db" not in g:
        conn = pymysql.connect(**get_db_config())
        g.db = DBWrapper(conn)
    return g.db


def init_db(app):
    config = get_db_config()

    # First connect without database to create it if needed
    conn = pymysql.connect(
        host=config["host"],
        user=config["user"],
        password=config["password"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )
    with conn.cursor() as cur:
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{config['database']}`")
    conn.close()

    # Now connect to the database and run schema
    conn = pymysql.connect(**config)
    with conn.cursor() as cur:
        schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "schema.sql")
        with open(schema_path, "r") as f:
            sql = f.read()
        for statement in sql.split(";"):
            statement = statement.strip()
            if statement:
                cur.execute(statement)
        conn.commit()

        # Check if sample data needs to be loaded
        cur.execute("SELECT COUNT(*) AS cnt FROM tickers")
        count = cur.fetchone()["cnt"]
        if count == 0:
            sample_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_data.sql")
            if os.path.exists(sample_path):
                from werkzeug.security import generate_password_hash
                admin_hash = generate_password_hash("admin123")

                demo_hash = generate_password_hash("demo123")

                with open(sample_path, "r") as f:
                    sql = f.read().replace("PLACEHOLDER_HASH", admin_hash).replace("DEMO_PLACEHOLDER_HASH", demo_hash)
                for statement in sql.split(";"):
                    statement = statement.strip()
                    if statement:
                        cur.execute(statement)
                conn.commit()

            # Create sample watchlists for admin user
            cur.execute("SELECT id FROM users WHERE email = 'admin@marketmonitor.com'")
            admin = cur.fetchone()
            if admin:
                admin_id = admin["id"]
                cur.execute("INSERT IGNORE INTO watchlists (user_id, name) VALUES (%s, 'Tech Stocks')", (admin_id,))
                cur.execute("INSERT IGNORE INTO watchlists (user_id, name) VALUES (%s, 'Finance')", (admin_id,))
                cur.execute("INSERT IGNORE INTO watchlists (user_id, name) VALUES (%s, 'Healthcare & Energy')", (admin_id,))
                conn.commit()

                cur.execute("SELECT id FROM watchlists WHERE user_id = %s AND name = 'Tech Stocks'", (admin_id,))
                tech_wl = cur.fetchone()
                cur.execute("SELECT id FROM watchlists WHERE user_id = %s AND name = 'Finance'", (admin_id,))
                fin_wl = cur.fetchone()
                cur.execute("SELECT id FROM watchlists WHERE user_id = %s AND name = 'Healthcare & Energy'", (admin_id,))
                health_wl = cur.fetchone()

                if tech_wl:
                    for sym in ["AAPL", "MSFT", "GOOGL", "NVDA", "META", "AMZN"]:
                        cur.execute("INSERT IGNORE INTO watchlist_items (watchlist_id, ticker_symbol) VALUES (%s, %s)", (tech_wl["id"], sym))

                if fin_wl:
                    for sym in ["JPM", "V", "GS", "BAC"]:
                        cur.execute("INSERT IGNORE INTO watchlist_items (watchlist_id, ticker_symbol) VALUES (%s, %s)", (fin_wl["id"], sym))

                if health_wl:
                    for sym in ["JNJ", "UNH", "XOM"]:
                        cur.execute("INSERT IGNORE INTO watchlist_items (watchlist_id, ticker_symbol) VALUES (%s, %s)", (health_wl["id"], sym))

                # Sample notes
                cur.execute("INSERT IGNORE INTO user_notes (user_id, ticker_symbol, note_text) VALUES (%s, 'AAPL', 'Strong services revenue growth. Watch for iPhone sales in Q2.')", (admin_id,))
                cur.execute("INSERT IGNORE INTO user_notes (user_id, ticker_symbol, note_text) VALUES (%s, 'NVDA', 'AI chip demand remains high. Data center revenue is key metric.')", (admin_id,))
                cur.execute("INSERT IGNORE INTO user_notes (user_id, ticker_symbol, note_text) VALUES (%s, 'TSLA', 'Delivery numbers coming soon. Cybertruck ramp-up is a wildcard.')", (admin_id,))
                cur.execute("INSERT IGNORE INTO user_notes (user_id, ticker_symbol, note_text) VALUES (%s, 'MSFT', 'Azure growth steady. Copilot monetization is the next catalyst.')", (admin_id,))
                cur.execute("INSERT IGNORE INTO user_notes (user_id, ticker_symbol, note_text) VALUES (%s, 'JPM', 'Interest rate environment favorable. Watch credit card delinquency trends.')", (admin_id,))
                cur.execute("INSERT IGNORE INTO user_notes (user_id, ticker_symbol, note_text) VALUES (%s, 'GOOGL', 'Search ad revenue still dominant. Cloud segment approaching profitability.')", (admin_id,))

                conn.commit()

    conn.close()
