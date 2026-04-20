from flask import Blueprint, request, session, jsonify
from ..db import get_db
from .auth import login_required

portfolio_bp = Blueprint("portfolio", __name__)


@portfolio_bp.route("", methods=["GET"])
@login_required
def get_portfolio():
    db = get_db()

    # Get all transactions grouped by symbol to calculate holdings
    rows = db.execute("""
        SELECT ticker_symbol, transaction_type, shares, price_per_share, transaction_date, id, notes
        FROM portfolio_transactions
        WHERE user_id = ?
        ORDER BY transaction_date DESC, created_at DESC
    """, (session["user_id"],)).fetchall()

    # Calculate holdings
    holdings = {}
    transactions = []

    for r in rows:
        transactions.append({
            "id": r["id"],
            "ticker_symbol": r["ticker_symbol"],
            "transaction_type": r["transaction_type"],
            "shares": r["shares"],
            "price_per_share": r["price_per_share"],
            "transaction_date": r["transaction_date"],
            "notes": r["notes"]
        })

        symbol = r["ticker_symbol"]
        if symbol not in holdings:
            holdings[symbol] = {"shares": 0, "total_cost": 0}

        if r["transaction_type"] == "buy":
            holdings[symbol]["shares"] += r["shares"]
            holdings[symbol]["total_cost"] += r["shares"] * r["price_per_share"]
        else:
            holdings[symbol]["shares"] -= r["shares"]
            # Reduce cost basis proportionally
            if holdings[symbol]["shares"] > 0:
                avg_cost = holdings[symbol]["total_cost"] / (holdings[symbol]["shares"] + r["shares"])
                holdings[symbol]["total_cost"] -= r["shares"] * avg_cost
            else:
                holdings[symbol]["total_cost"] = 0

    # Build summary with ticker info
    summary = []
    for symbol, data in holdings.items():
        if data["shares"] > 0:
            ticker = db.execute("SELECT name, sector FROM tickers WHERE symbol = ?", (symbol,)).fetchone()
            avg_cost = data["total_cost"] / data["shares"] if data["shares"] > 0 else 0
            summary.append({
                "symbol": symbol,
                "name": ticker["name"] if ticker else symbol,
                "sector": ticker["sector"] if ticker else None,
                "shares": round(data["shares"], 4),
                "avg_cost": round(avg_cost, 2),
                "total_cost": round(data["total_cost"], 2)
            })

    summary.sort(key=lambda x: x["total_cost"], reverse=True)

    return jsonify({"holdings": summary, "transactions": transactions})


@portfolio_bp.route("", methods=["POST"])
@login_required
def add_transaction():
    data = request.get_json()
    required = ["ticker_symbol", "transaction_type", "shares", "price_per_share", "transaction_date"]
    if not data or not all(data.get(f) for f in required):
        return jsonify({"error": "ticker_symbol, transaction_type, shares, price_per_share, and transaction_date are required"}), 400

    symbol = data["ticker_symbol"].strip().upper()
    tx_type = data["transaction_type"]
    if tx_type not in ("buy", "sell"):
        return jsonify({"error": "transaction_type must be 'buy' or 'sell'"}), 400

    shares = float(data["shares"])
    price = float(data["price_per_share"])
    if shares <= 0 or price <= 0:
        return jsonify({"error": "Shares and price must be positive"}), 400

    db = get_db()

    # Ensure ticker exists
    ticker = db.execute("SELECT symbol FROM tickers WHERE symbol = ?", (symbol,)).fetchone()
    if not ticker:
        db.execute("INSERT INTO tickers (symbol, name) VALUES (?, ?)", (symbol, symbol))

    # For sells, check we have enough shares
    if tx_type == "sell":
        held = db.execute("""
            SELECT COALESCE(SUM(CASE WHEN transaction_type='buy' THEN shares ELSE -shares END), 0) as total
            FROM portfolio_transactions
            WHERE user_id = ? AND ticker_symbol = ?
        """, (session["user_id"], symbol)).fetchone()
        if held["total"] < shares:
            return jsonify({"error": f"Cannot sell {shares} shares — you only hold {held['total']}"}), 400

    cursor = db.execute("""
        INSERT INTO portfolio_transactions (user_id, ticker_symbol, transaction_type, shares, price_per_share, transaction_date, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (session["user_id"], symbol, tx_type, shares, price, data["transaction_date"], data.get("notes", "")))
    db.commit()

    return jsonify({"id": cursor.lastrowid, "message": f"{tx_type.capitalize()} recorded"}), 201


@portfolio_bp.route("/<int:transaction_id>", methods=["DELETE"])
@login_required
def delete_transaction(transaction_id):
    db = get_db()
    tx = db.execute("SELECT * FROM portfolio_transactions WHERE id = ? AND user_id = ?", (transaction_id, session["user_id"])).fetchone()
    if not tx:
        return jsonify({"error": "Transaction not found"}), 404

    db.execute("DELETE FROM portfolio_transactions WHERE id = ?", (transaction_id,))
    db.commit()

    return jsonify({"message": "Transaction deleted"})
