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


@market_bp.route("/economics", methods=["GET"])
def economics():
    db = get_db()

    indicators = {}

    # Federal Funds Rate
    cache_key = "av:federal_funds_rate"
    cached = get_cached(db, cache_key)
    if cached:
        indicators["fed_funds_rate"] = cached
    elif ALPHA_VANTAGE_KEY:
        try:
            url = f"https://www.alphavantage.co/query?function=FEDERAL_FUNDS_RATE&apikey={ALPHA_VANTAGE_KEY}"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            if "data" in data and len(data["data"]) > 0:
                latest = data["data"][0]
                result = {"value": latest["value"], "date": latest["date"]}
                set_cached(db, cache_key, result, minutes=1440)
                indicators["fed_funds_rate"] = result
        except Exception:
            pass

    # Treasury Yields (2Y, 5Y, 10Y)
    for maturity in ["2year", "5year", "10year"]:
        cache_key = f"av:treasury_yield:{maturity}"
        cached = get_cached(db, cache_key)
        if cached:
            indicators[f"treasury_{maturity}"] = cached
        elif ALPHA_VANTAGE_KEY:
            try:
                url = f"https://www.alphavantage.co/query?function=TREASURY_YIELD&interval=daily&maturity={maturity}&apikey={ALPHA_VANTAGE_KEY}"
                resp = requests.get(url, timeout=10)
                data = resp.json()
                if "data" in data and len(data["data"]) > 0:
                    latest = data["data"][0]
                    result = {"value": latest["value"], "date": latest["date"]}
                    set_cached(db, cache_key, result, minutes=1440)
                    indicators[f"treasury_{maturity}"] = result
                time.sleep(1)
            except Exception:
                pass

    # US Inflation (annual)
    cache_key = "av:inflation"
    cached = get_cached(db, cache_key)
    if cached:
        indicators["inflation"] = cached
    elif ALPHA_VANTAGE_KEY:
        try:
            url = f"https://www.alphavantage.co/query?function=INFLATION&apikey={ALPHA_VANTAGE_KEY}"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            if "data" in data and len(data["data"]) > 0:
                latest = data["data"][0]
                result = {"value": latest["value"], "date": latest["date"]}
                set_cached(db, cache_key, result, minutes=1440)
                indicators["inflation"] = result
            time.sleep(1)
        except Exception:
            pass

    # CPI (monthly)
    cache_key = "av:cpi"
    cached = get_cached(db, cache_key)
    if cached:
        indicators["cpi"] = cached
    elif ALPHA_VANTAGE_KEY:
        try:
            url = f"https://www.alphavantage.co/query?function=CPI&interval=monthly&apikey={ALPHA_VANTAGE_KEY}"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            if "data" in data and len(data["data"]) > 0:
                latest = data["data"][0]
                result = {"value": latest["value"], "date": latest["date"]}
                set_cached(db, cache_key, result, minutes=1440)
                indicators["cpi"] = result
            time.sleep(1)
        except Exception:
            pass

    # Unemployment Rate
    cache_key = "av:unemployment"
    cached = get_cached(db, cache_key)
    if cached:
        indicators["unemployment"] = cached
    elif ALPHA_VANTAGE_KEY:
        try:
            url = f"https://www.alphavantage.co/query?function=UNEMPLOYMENT&apikey={ALPHA_VANTAGE_KEY}"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            if "data" in data and len(data["data"]) > 0:
                latest = data["data"][0]
                result = {"value": latest["value"], "date": latest["date"]}
                set_cached(db, cache_key, result, minutes=1440)
                indicators["unemployment"] = result
            time.sleep(1)
        except Exception:
            pass

    # US Real GDP (quarterly)
    cache_key = "av:real_gdp"
    cached = get_cached(db, cache_key)
    if cached:
        indicators["us_gdp"] = cached
    elif ALPHA_VANTAGE_KEY:
        try:
            url = f"https://www.alphavantage.co/query?function=REAL_GDP&interval=quarterly&apikey={ALPHA_VANTAGE_KEY}"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            if "data" in data and len(data["data"]) > 0:
                latest = data["data"][0]
                result = {"value": latest["value"], "date": latest["date"]}
                set_cached(db, cache_key, result, minutes=1440)
                indicators["us_gdp"] = result
        except Exception:
            pass

    # International GDP from World Bank (free, no key)
    gdp_countries = [
        ("GBR", "United Kingdom"),
        ("DEU", "Germany"),
        ("JPN", "Japan"),
        ("CAN", "Canada"),
        ("FRA", "France"),
    ]
    intl_gdp = []
    cache_key = "worldbank:gdp_intl"
    cached = get_cached(db, cache_key)
    if cached:
        intl_gdp = cached
    else:
        country_codes = ";".join([c[0] for c in gdp_countries])
        try:
            url = f"https://api.worldbank.org/v2/country/{country_codes}/indicator/NY.GDP.MKTP.CD?format=json&date=2020:2024&per_page=100"
            resp = requests.get(url, timeout=15)
            data = resp.json()
            if len(data) > 1 and data[1]:
                latest_by_country = {}
                for entry in data[1]:
                    code = entry["country"]["id"]
                    if code not in latest_by_country and entry["value"] is not None:
                        latest_by_country[code] = {
                            "country": entry["country"]["value"],
                            "code": code,
                            "value": entry["value"],
                            "year": entry["date"]
                        }
                for code, name in gdp_countries:
                    if code in latest_by_country:
                        intl_gdp.append(latest_by_country[code])
                if intl_gdp:
                    set_cached(db, cache_key, intl_gdp, minutes=1440)
        except Exception:
            pass
    indicators["intl_gdp"] = intl_gdp

    return jsonify(indicators)


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
