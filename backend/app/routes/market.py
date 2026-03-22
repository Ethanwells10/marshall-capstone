from flask import Blueprint, jsonify
from ..db import get_db
from ..services.cache import get_cached, set_cached
import requests
import os

market_bp = Blueprint("market", __name__)

ALPHA_VANTAGE_KEY = os.environ.get("ALPHA_VANTAGE_KEY", "")


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

    for symbol, name in index_symbols:
        cache_key = f"alphavantage:quote:{symbol}"
        cached = get_cached(db, cache_key)
        if cached:
            indices.append({"symbol": symbol, "name": name, **cached})
        elif ALPHA_VANTAGE_KEY:
            try:
                url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_KEY}"
                resp = requests.get(url, timeout=10)
                data = resp.json()
                gq = data.get("Global Quote", {})
                if gq:
                    quote = {
                        "price": float(gq.get("05. price", 0)),
                        "change_percent": float(gq.get("10. change percent", "0%").replace("%", ""))
                    }
                    indices.append({"symbol": symbol, "name": name, **quote})
                    set_cached(db, cache_key, quote, minutes=15)
            except Exception:
                indices.append({"symbol": symbol, "name": name, "price": None, "change_percent": None})
        else:
            indices.append({"symbol": symbol, "name": name, "price": None, "change_percent": None})

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
