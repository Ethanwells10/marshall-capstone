from flask import Blueprint, jsonify
from ..db import get_db
from ..services.cache import get_cached, set_cached
import requests
import os
import time

market_bp = Blueprint("market", __name__)

ALPHA_VANTAGE_KEY = os.environ.get("ALPHA_VANTAGE_KEY", "")
FINNHUB_KEY = os.environ.get("FINNHUB_KEY", "")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "")


def fetch_quote(symbol, db):
    """Fetch a quote from cache, then Finnhub, then Alpha Vantage."""
    cache_key = f"alphavantage:quote:{symbol}"
    cached = get_cached(db, cache_key)
    if cached:
        return cached

    # Try Finnhub first (60 req/min)
    if FINNHUB_KEY:
        try:
            url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_KEY}"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            if data.get("c") and data["c"] > 0:
                quote = {
                    "price": data["c"],
                    "change": round(data["c"] - data["pc"], 2),
                    "change_percent": round(((data["c"] - data["pc"]) / data["pc"]) * 100, 2),
                    "volume": 0
                }
                set_cached(db, cache_key, quote, minutes=60)
                return quote
        except Exception:
            pass

    # Fallback to Alpha Vantage (25 req/day)
    if ALPHA_VANTAGE_KEY:
        try:
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_KEY}"
            resp = requests.get(url, timeout=10)
            data = resp.json()

            if "Information" in data or "Note" in data:
                return None

            gq = data.get("Global Quote", {})
            if gq and gq.get("05. price"):
                quote = {
                    "price": float(gq.get("05. price", 0)),
                    "change": float(gq.get("09. change", 0)),
                    "change_percent": float(gq.get("10. change percent", "0%").replace("%", "")),
                    "volume": int(gq.get("06. volume", 0))
                }
                set_cached(db, cache_key, quote, minutes=60)
                return quote
        except Exception:
            pass

    return None


@market_bp.route("/overview", methods=["GET"])
def overview():
    db = get_db()

    # Get index ETF data
    indices = []
    index_symbols = [
        ("SPY", "S&P 500 ETF"),
        ("QQQ", "Nasdaq 100 ETF"),
        ("DIA", "Dow Jones ETF")
    ]

    for i, (symbol, name) in enumerate(index_symbols):
        quote = fetch_quote(symbol, db)
        if quote:
            indices.append({"symbol": symbol, "name": name, **quote})
        else:
            indices.append({"symbol": symbol, "name": name, "price": None, "change_percent": None})

        # Rate limit: wait between uncached API calls (only for Alpha Vantage fallback)
        if not FINNHUB_KEY and i < len(index_symbols) - 1:
            cache_key = f"alphavantage:quote:{index_symbols[i+1][0]}"
            if not get_cached(db, cache_key):
                time.sleep(1.5)

    # Get crypto data from CoinGecko
    crypto = []
    cache_key = "coingecko:prices"
    cached = get_cached(db, cache_key)
    if cached:
        crypto = cached
    else:
        try:
            url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,cardano&vs_currencies=usd&include_24hr_change=true"
            resp = requests.get(url, timeout=10)
            data = resp.json()

            crypto_map = [
                ("bitcoin", "BTC", "Bitcoin"),
                ("ethereum", "ETH", "Ethereum"),
                ("cardano", "ADA", "Cardano")
            ]

            for coin_id, symbol, name in crypto_map:
                coin = data.get(coin_id, {})
                crypto.append({
                    "id": coin_id,
                    "symbol": symbol,
                    "name": name,
                    "price": coin.get("usd"),
                    "change_percent_24h": round(coin.get("usd_24h_change", 0), 2)
                })

            if crypto:
                set_cached(db, cache_key, crypto, minutes=5)
        except Exception:
            crypto = [
                {"id": "bitcoin", "symbol": "BTC", "name": "Bitcoin", "price": None, "change_percent_24h": None},
                {"id": "ethereum", "symbol": "ETH", "name": "Ethereum", "price": None, "change_percent_24h": None},
                {"id": "cardano", "symbol": "ADA", "name": "Cardano", "price": None, "change_percent_24h": None}
            ]

    return jsonify({"indices": indices, "crypto": crypto})


@market_bp.route("/headlines", methods=["GET"])
def headlines():
    db = get_db()

    cache_key = "newsapi:top_headlines"
    cached = get_cached(db, cache_key)
    if cached:
        return jsonify({"articles": cached})

    articles = []
    if NEWS_API_KEY:
        try:
            url = f"https://newsapi.org/v2/top-headlines?category=business&country=us&pageSize=6&apiKey={NEWS_API_KEY}"
            resp = requests.get(url, timeout=10)
            data = resp.json()

            for article in data.get("articles", [])[:6]:
                articles.append({
                    "title": article.get("title"),
                    "source": article.get("source", {}).get("name"),
                    "url": article.get("url"),
                    "published_at": article.get("publishedAt"),
                    "description": article.get("description")
                })

            if articles:
                set_cached(db, cache_key, articles, minutes=30)
        except Exception:
            pass

    return jsonify({"articles": articles})
