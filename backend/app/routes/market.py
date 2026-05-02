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
FRED_API_KEY = os.environ.get("FRED_API_KEY", "")


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


def fetch_fred_series(db, series_id):
    """Fetch the latest observation from FRED API with caching."""
    cache_key = f"fred:{series_id}"
    cached = get_cached(db, cache_key)
    if cached:
        return cached

    if not FRED_API_KEY:
        return None

    try:
        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id={series_id}&api_key={FRED_API_KEY}"
            f"&file_type=json&sort_order=desc&limit=5"
        )
        resp = requests.get(url, timeout=10)
        data = resp.json()
        observations = data.get("observations", [])
        for obs in observations:
            if obs["value"] != ".":
                result = {"value": round(float(obs["value"]), 1), "date": obs["date"]}
                set_cached(db, cache_key, result, minutes=720)
                return result
    except Exception:
        pass
    return None


@market_bp.route("/economics", methods=["GET"])
def economics():
    db = get_db()

    indicators = {}

    fred_series = {
        "fed_funds_rate": "DFF",
        "treasury_2year": "DGS2",
        "treasury_5year": "DGS5",
        "treasury_10year": "DGS10",
        "nominal_gdp": "GDP",
        "real_gdp": "GDPC1",
        "gdp_growth_rate": "A191RL1Q225SBEA",
        "cpi": "CPIAUCSL",
        "unemployment": "UNRATE",
    }

    for key, series_id in fred_series.items():
        result = fetch_fred_series(db, series_id)
        if result:
            indicators[key] = result

    # Inflation rate: CPI percent change from year ago (most current measure)
    cache_key = "fred:inflation_pc1"
    cached = get_cached(db, cache_key)
    if cached:
        indicators["inflation"] = cached
    elif FRED_API_KEY:
        try:
            url = (
                f"https://api.stlouisfed.org/fred/series/observations"
                f"?series_id=CPIAUCSL&api_key={FRED_API_KEY}"
                f"&file_type=json&sort_order=desc&limit=5&units=pc1"
            )
            resp = requests.get(url, timeout=10)
            data = resp.json()
            observations = data.get("observations", [])
            for obs in observations:
                if obs["value"] != ".":
                    result = {"value": round(float(obs["value"]), 1), "date": obs["date"]}
                    set_cached(db, cache_key, result, minutes=720)
                    indicators["inflation"] = result
                    break
        except Exception:
            pass

    # International GDP from IMF DataMapper (free, no key, has current year estimates)
    gdp_countries = [
        ("USA", "United States"),
        ("CHN", "China"),
        ("DEU", "Germany"),
        ("JPN", "Japan"),
        ("GBR", "United Kingdom"),
        ("FRA", "France"),
        ("CAN", "Canada"),
    ]
    intl_gdp = []
    cache_key = "imf:gdp_intl"
    cached = get_cached(db, cache_key)
    if cached:
        intl_gdp = cached
    else:
        country_path = "/".join([c[0] for c in gdp_countries])
        try:
            url = f"https://www.imf.org/external/datamapper/api/v1/NGDPD/{country_path}"
            resp = requests.get(url, timeout=15)
            data = resp.json()
            gdp_values = data.get("values", {}).get("NGDPD", {})
            for code, name in gdp_countries:
                years = gdp_values.get(code, {})
                for yr in ["2026", "2025", "2024"]:
                    if yr in years and years[yr] is not None:
                        intl_gdp.append({
                            "country": name,
                            "code": code,
                            "value": round(years[yr] * 1e9, 1),
                            "year": yr,
                        })
                        break
            if intl_gdp:
                set_cached(db, cache_key, intl_gdp, minutes=1440)
        except Exception:
            pass
    indicators["intl_gdp"] = intl_gdp

    return jsonify(indicators)


@market_bp.route("/economics/news", methods=["GET"])
def economics_news():
    """Fetch news related to a specific economic topic."""
    from flask import request as req
    db = get_db()
    topic = req.args.get("topic", "economy")

    cache_key = f"newsapi:econ:{topic}"
    cached = get_cached(db, cache_key)
    if cached:
        return jsonify({"articles": cached})

    articles = []
    if NEWS_API_KEY:
        try:
            url = (
                f"https://newsapi.org/v2/everything"
                f"?q={topic}&language=en&sortBy=publishedAt&pageSize=5"
                f"&apiKey={NEWS_API_KEY}"
            )
            resp = requests.get(url, timeout=10)
            data = resp.json()
            for article in data.get("articles", [])[:5]:
                articles.append({
                    "title": article.get("title"),
                    "source": article.get("source", {}).get("name"),
                    "url": article.get("url"),
                    "published_at": article.get("publishedAt"),
                    "description": article.get("description"),
                })
            if articles:
                set_cached(db, cache_key, articles, minutes=60)
        except Exception:
            pass

    return jsonify({"articles": articles})


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
