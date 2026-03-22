from flask import Blueprint, request, session, jsonify
from ..db import get_db
from .auth import login_required

watchlists_bp = Blueprint("watchlists", __name__)


@watchlists_bp.route("", methods=["GET"])
@login_required
def get_watchlists():
    db = get_db()
    rows = db.execute("""
        SELECT w.id, w.name, w.created_at, COUNT(wi.id) as item_count
        FROM watchlists w
        LEFT JOIN watchlist_items wi ON w.id = wi.watchlist_id
        WHERE w.user_id = ?
        GROUP BY w.id
        ORDER BY w.created_at DESC
    """, (session["user_id"],)).fetchall()

    watchlists = [{"id": r["id"], "name": r["name"], "item_count": r["item_count"], "created_at": r["created_at"]} for r in rows]
    return jsonify({"watchlists": watchlists})


@watchlists_bp.route("", methods=["POST"])
@login_required
def create_watchlist():
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "Name is required"}), 400

    name = data["name"].strip()
    db = get_db()

    existing = db.execute(
        "SELECT id FROM watchlists WHERE user_id = ? AND name = ?",
        (session["user_id"], name)
    ).fetchone()
    if existing:
        return jsonify({"error": "Watchlist with this name already exists"}), 409

    cursor = db.execute(
        "INSERT INTO watchlists (user_id, name) VALUES (?, ?)",
        (session["user_id"], name)
    )
    db.commit()

    return jsonify({"id": cursor.lastrowid, "name": name, "created_at": None}), 201


@watchlists_bp.route("/<int:watchlist_id>", methods=["PUT"])
@login_required
def update_watchlist(watchlist_id):
    db = get_db()
    wl = db.execute("SELECT * FROM watchlists WHERE id = ? AND user_id = ?", (watchlist_id, session["user_id"])).fetchone()
    if not wl:
        return jsonify({"error": "Watchlist not found"}), 404

    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "Name is required"}), 400

    name = data["name"].strip()

    existing = db.execute(
        "SELECT id FROM watchlists WHERE user_id = ? AND name = ? AND id != ?",
        (session["user_id"], name, watchlist_id)
    ).fetchone()
    if existing:
        return jsonify({"error": "Watchlist with this name already exists"}), 409

    db.execute("UPDATE watchlists SET name = ? WHERE id = ?", (name, watchlist_id))
    db.commit()

    return jsonify({"id": watchlist_id, "name": name})


@watchlists_bp.route("/<int:watchlist_id>", methods=["DELETE"])
@login_required
def delete_watchlist(watchlist_id):
    db = get_db()
    wl = db.execute("SELECT * FROM watchlists WHERE id = ? AND user_id = ?", (watchlist_id, session["user_id"])).fetchone()
    if not wl:
        return jsonify({"error": "Watchlist not found"}), 404

    db.execute("DELETE FROM watchlists WHERE id = ?", (watchlist_id,))
    db.commit()

    return jsonify({"message": "Watchlist deleted"})


@watchlists_bp.route("/<int:watchlist_id>/items", methods=["GET"])
@login_required
def get_watchlist_items(watchlist_id):
    db = get_db()
    wl = db.execute("SELECT * FROM watchlists WHERE id = ? AND user_id = ?", (watchlist_id, session["user_id"])).fetchone()
    if not wl:
        return jsonify({"error": "Watchlist not found"}), 404

    rows = db.execute("""
        SELECT t.symbol, t.name, t.exchange, t.sector, t.industry
        FROM watchlist_items wi
        JOIN tickers t ON wi.ticker_symbol = t.symbol
        WHERE wi.watchlist_id = ?
        ORDER BY t.symbol
    """, (watchlist_id,)).fetchall()

    items = [{"symbol": r["symbol"], "name": r["name"], "exchange": r["exchange"], "sector": r["sector"], "industry": r["industry"]} for r in rows]

    return jsonify({
        "watchlist": {"id": wl["id"], "name": wl["name"]},
        "items": items
    })


@watchlists_bp.route("/<int:watchlist_id>/items", methods=["POST"])
@login_required
def add_watchlist_item(watchlist_id):
    db = get_db()
    wl = db.execute("SELECT * FROM watchlists WHERE id = ? AND user_id = ?", (watchlist_id, session["user_id"])).fetchone()
    if not wl:
        return jsonify({"error": "Watchlist not found"}), 404

    data = request.get_json()
    if not data or not data.get("symbol"):
        return jsonify({"error": "Symbol is required"}), 400

    symbol = data["symbol"].strip().upper()

    # Check if ticker exists, if not create it
    ticker = db.execute("SELECT symbol FROM tickers WHERE symbol = ?", (symbol,)).fetchone()
    if not ticker:
        db.execute("INSERT INTO tickers (symbol, name) VALUES (?, ?)", (symbol, symbol))

    # Check if already in watchlist
    existing = db.execute(
        "SELECT id FROM watchlist_items WHERE watchlist_id = ? AND ticker_symbol = ?",
        (watchlist_id, symbol)
    ).fetchone()
    if existing:
        return jsonify({"error": "Ticker already in watchlist"}), 409

    db.execute(
        "INSERT INTO watchlist_items (watchlist_id, ticker_symbol) VALUES (?, ?)",
        (watchlist_id, symbol)
    )
    db.commit()

    return jsonify({"message": f"{symbol} added to watchlist", "symbol": symbol}), 201


@watchlists_bp.route("/<int:watchlist_id>/items/<symbol>", methods=["DELETE"])
@login_required
def remove_watchlist_item(watchlist_id, symbol):
    db = get_db()
    wl = db.execute("SELECT * FROM watchlists WHERE id = ? AND user_id = ?", (watchlist_id, session["user_id"])).fetchone()
    if not wl:
        return jsonify({"error": "Watchlist not found"}), 404

    symbol = symbol.upper()
    item = db.execute(
        "SELECT id FROM watchlist_items WHERE watchlist_id = ? AND ticker_symbol = ?",
        (watchlist_id, symbol)
    ).fetchone()
    if not item:
        return jsonify({"error": "Ticker not in watchlist"}), 404

    db.execute("DELETE FROM watchlist_items WHERE id = ?", (item["id"],))
    db.commit()

    return jsonify({"message": f"{symbol} removed from watchlist"})
