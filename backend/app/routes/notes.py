from flask import Blueprint, request, session, jsonify
from ..db import get_db
from .auth import login_required

notes_bp = Blueprint("notes", __name__)


@notes_bp.route("", methods=["GET"])
@login_required
def get_notes():
    db = get_db()
    symbol = request.args.get("symbol")

    if symbol:
        rows = db.execute("""
            SELECT id, ticker_symbol, note_text, created_at, updated_at
            FROM user_notes
            WHERE user_id = ? AND ticker_symbol = ?
            ORDER BY updated_at DESC
        """, (session["user_id"], symbol.upper())).fetchall()
    else:
        rows = db.execute("""
            SELECT id, ticker_symbol, note_text, created_at, updated_at
            FROM user_notes
            WHERE user_id = ?
            ORDER BY updated_at DESC
        """, (session["user_id"],)).fetchall()

    notes = [{"id": r["id"], "ticker_symbol": r["ticker_symbol"], "note_text": r["note_text"], "created_at": r["created_at"], "updated_at": r["updated_at"]} for r in rows]
    return jsonify({"notes": notes})


@notes_bp.route("", methods=["POST"])
@login_required
def create_note():
    data = request.get_json()
    if not data or not data.get("ticker_symbol") or not data.get("note_text"):
        return jsonify({"error": "ticker_symbol and note_text are required"}), 400

    symbol = data["ticker_symbol"].strip().upper()
    note_text = data["note_text"].strip()
    db = get_db()

    # Ensure ticker exists
    ticker = db.execute("SELECT symbol FROM tickers WHERE symbol = ?", (symbol,)).fetchone()
    if not ticker:
        db.execute("INSERT INTO tickers (symbol, name) VALUES (?, ?)", (symbol, symbol))

    cursor = db.execute(
        "INSERT INTO user_notes (user_id, ticker_symbol, note_text) VALUES (?, ?, ?)",
        (session["user_id"], symbol, note_text)
    )
    db.commit()

    return jsonify({
        "id": cursor.lastrowid,
        "ticker_symbol": symbol,
        "note_text": note_text,
        "created_at": None
    }), 201


@notes_bp.route("/<int:note_id>", methods=["PUT"])
@login_required
def update_note(note_id):
    db = get_db()
    note = db.execute("SELECT * FROM user_notes WHERE id = ? AND user_id = ?", (note_id, session["user_id"])).fetchone()
    if not note:
        return jsonify({"error": "Note not found"}), 404

    data = request.get_json()
    if not data or not data.get("note_text"):
        return jsonify({"error": "note_text is required"}), 400

    note_text = data["note_text"].strip()
    db.execute(
        "UPDATE user_notes SET note_text = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (note_text, note_id)
    )
    db.commit()

    return jsonify({"id": note_id, "note_text": note_text, "updated_at": None})


@notes_bp.route("/<int:note_id>", methods=["DELETE"])
@login_required
def delete_note(note_id):
    db = get_db()
    note = db.execute("SELECT * FROM user_notes WHERE id = ? AND user_id = ?", (note_id, session["user_id"])).fetchone()
    if not note:
        return jsonify({"error": "Note not found"}), 404

    db.execute("DELETE FROM user_notes WHERE id = ?", (note_id,))
    db.commit()

    return jsonify({"message": "Note deleted"})
