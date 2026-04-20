from flask import Blueprint, jsonify, request
from ..db import get_db
from ..services.cache import get_cached, set_cached
import requests
import os
import time

stocks_bp = Blueprint("stocks", __name__)

ALPHA_VANTAGE_KEY = os.environ.get("ALPHA_VANTAGE_KEY", "")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "")


@stocks_bp.route("/browse", methods=["GET"])
def browse_stocks():
    db = get_db()
    rows = db.execute("""
        SELECT symbol, name, exchange, sector, industry
        FROM tickers
        WHERE name IS NOT NULL AND name != symbol
        ORDER BY symbol
    """).fetchall()

    tickers = [{"symbol": r["symbol"], "name": r["name"], "exchange": r["exchange"], "sector": r["sector"], "industry": r["industry"]} for r in rows]
    return jsonify({"tickers": tickers})


@stocks_bp.route("/search", methods=["GET"])
def search_stocks():
    q = request.args.get("q", "").strip().upper()
    if not q:
        return jsonify({"results": []})

    db = get_db()
    rows = db.execute("""
        SELECT symbol, name, exchange, sector, industry
        FROM tickers
        WHERE symbol LIKE ? OR UPPER(name) LIKE ?
        ORDER BY CASE WHEN symbol = ? THEN 0 WHEN symbol LIKE ? THEN 1 ELSE 2 END
        LIMIT 20
    """, (f"%{q}%", f"%{q}%", q, f"{q}%")).fetchall()

    results = [{"symbol": r["symbol"], "name": r["name"], "exchange": r["exchange"], "sector": r["sector"], "industry": r["industry"]} for r in rows]
    return jsonify({"results": results, "query": q})


@stocks_bp.route("/<symbol>", methods=["GET"])
def get_stock(symbol):
    symbol = symbol.upper()
    db = get_db()

    # Get ticker from database
    ticker = db.execute("SELECT * FROM tickers WHERE symbol = ?", (symbol,)).fetchone()

    stock_data = {
        "symbol": symbol,
        "name": ticker["name"] if ticker else symbol,
        "exchange": ticker["exchange"] if ticker else None,
        "sector": ticker["sector"] if ticker else None,
        "industry": ticker["industry"] if ticker else None,
        "quote": None
    }

    # Try to get live quote from cache or API
    cache_key = f"alphavantage:quote:{symbol}"
    cached = get_cached(db, cache_key)
    if cached:
        stock_data["quote"] = cached
    elif ALPHA_VANTAGE_KEY:
        try:
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_KEY}"
            resp = requests.get(url, timeout=10)
            data = resp.json()

            # Handle rate limit
            if "Information" in data or "Note" in data:
                stock_data["rate_limited"] = True
            else:
                gq = data.get("Global Quote", {})
                if gq and gq.get("05. price"):
                    quote = {
                        "price": float(gq.get("05. price", 0)),
                        "change": float(gq.get("09. change", 0)),
                        "change_percent": gq.get("10. change percent", "0%").replace("%", ""),
                        "volume": int(gq.get("06. volume", 0))
                    }
                    stock_data["quote"] = quote
                    set_cached(db, cache_key, quote, minutes=60)
        except Exception:
            pass

    return jsonify(stock_data)


@stocks_bp.route("/<symbol>/history", methods=["GET"])
def get_stock_history(symbol):
    symbol = symbol.upper()
    time_range = request.args.get("range", "1M")
    db = get_db()

    cache_key = f"alphavantage:history:{symbol}:{time_range}"
    cached = get_cached(db, cache_key)
    if cached:
        return jsonify({"symbol": symbol, "range": time_range, "prices": cached})

    prices = []
    if ALPHA_VANTAGE_KEY:
        try:
            if time_range in ("1W", "1M"):
                function = "TIME_SERIES_DAILY"
            else:
                function = "TIME_SERIES_WEEKLY"

            url = f"https://www.alphavantage.co/query?function={function}&symbol={symbol}&apikey={ALPHA_VANTAGE_KEY}"
            resp = requests.get(url, timeout=10)
            data = resp.json()

            # Handle rate limit
            if "Information" in data or "Note" in data:
                return jsonify({"symbol": symbol, "range": time_range, "prices": [], "rate_limited": True})

            time_series_key = "Time Series (Daily)" if function == "TIME_SERIES_DAILY" else "Weekly Time Series"
            series = data.get(time_series_key, {})

            limit = {"1W": 5, "1M": 22, "3M": 66, "1Y": 52}.get(time_range, 22)

            for date, values in sorted(series.items(), reverse=True)[:limit]:
                prices.append({"date": date, "close": float(values["4. close"])})

            prices.reverse()

            if prices:
                set_cached(db, cache_key, prices, minutes=1440)
        except Exception:
            pass

    return jsonify({"symbol": symbol, "range": time_range, "prices": prices})


@stocks_bp.route("/<symbol>/news", methods=["GET"])
def get_stock_news(symbol):
    symbol = symbol.upper()
    db = get_db()

    cache_key = f"newsapi:headlines:{symbol}"
    cached = get_cached(db, cache_key)
    if cached:
        return jsonify({"symbol": symbol, "articles": cached})

    articles = []
    if NEWS_API_KEY:
        try:
            url = f"https://newsapi.org/v2/everything?q={symbol}+stock&sortBy=publishedAt&pageSize=5&apiKey={NEWS_API_KEY}"
            resp = requests.get(url, timeout=10)
            data = resp.json()

            for article in data.get("articles", [])[:5]:
                articles.append({
                    "title": article.get("title"),
                    "source": article.get("source", {}).get("name"),
                    "url": article.get("url"),
                    "published_at": article.get("publishedAt")
                })

            if articles:
                set_cached(db, cache_key, articles, minutes=60)
        except Exception:
            pass

    return jsonify({"symbol": symbol, "articles": articles})
