"""
Local Market Price Checker API
--------------------------------
A simple REST API that lets people report and look up prices of
everyday items (food, commodities, etc.) across different local markets.

Problem it solves: Buyers and traders in Nigerian markets often lack an
easy way to check what an item "should" cost across nearby markets,
which makes it easier to get overcharged. This app lets anyone submit
a price report and lets anyone else search reported prices by item,
market, or location.

Endpoints:
    GET  /                          -> health check
    POST /prices                    -> add a new price report
    GET  /prices                    -> list/search price reports
                                        (optional query params: item, market, location)
    GET  /prices/<id>               -> get a single price report
    DELETE /prices/<id>             -> remove a price report
"""

import os
import sqlite3
from datetime import datetime, timezone
from flask import Flask, request, jsonify, g

app = Flask(__name__)

DB_PATH = os.environ.get("DB_PATH", "market_prices.db")


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    # Use a standalone connection here since this can run outside a request context.
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT NOT NULL,
            market TEXT NOT NULL,
            location TEXT NOT NULL,
            price REAL NOT NULL,
            unit TEXT,
            reported_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def row_to_dict(row):
    return {
        "id": row["id"],
        "item": row["item"],
        "market": row["market"],
        "location": row["location"],
        "price": row["price"],
        "unit": row["unit"],
        "reported_at": row["reported_at"],
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "service": "market-price-checker"}), 200


@app.route("/prices", methods=["POST"])
def add_price():
    data = request.get_json(silent=True) or {}

    required_fields = ["item", "market", "location", "price"]
    missing = [f for f in required_fields if f not in data or data[f] in (None, "")]
    if missing:
        return jsonify({"error": f"Missing required field(s): {', '.join(missing)}"}), 400

    try:
        price = float(data["price"])
    except (TypeError, ValueError):
        return jsonify({"error": "price must be a number"}), 400

    if price < 0:
        return jsonify({"error": "price cannot be negative"}), 400

    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO prices (item, market, location, price, unit, reported_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            data["item"].strip(),
            data["market"].strip(),
            data["location"].strip(),
            price,
            (data.get("unit") or "").strip() or None,
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    db.commit()

    new_row = db.execute("SELECT * FROM prices WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return jsonify(row_to_dict(new_row)), 201


@app.route("/prices", methods=["GET"])
def list_prices():
    item = request.args.get("item")
    market = request.args.get("market")
    location = request.args.get("location")

    query = "SELECT * FROM prices WHERE 1=1"
    params = []

    if item:
        query += " AND item LIKE ?"
        params.append(f"%{item}%")
    if market:
        query += " AND market LIKE ?"
        params.append(f"%{market}%")
    if location:
        query += " AND location LIKE ?"
        params.append(f"%{location}%")

    query += " ORDER BY reported_at DESC"

    db = get_db()
    rows = db.execute(query, params).fetchall()
    return jsonify([row_to_dict(r) for r in rows]), 200


@app.route("/prices/<int:price_id>", methods=["GET"])
def get_price(price_id):
    db = get_db()
    row = db.execute("SELECT * FROM prices WHERE id = ?", (price_id,)).fetchone()
    if row is None:
        return jsonify({"error": "Price report not found"}), 404
    return jsonify(row_to_dict(row)), 200


@app.route("/prices/<int:price_id>", methods=["DELETE"])
def delete_price(price_id):
    db = get_db()
    row = db.execute("SELECT * FROM prices WHERE id = ?", (price_id,)).fetchone()
    if row is None:
        return jsonify({"error": "Price report not found"}), 404

    db.execute("DELETE FROM prices WHERE id = ?", (price_id,))
    db.commit()
    return jsonify({"message": f"Price report {price_id} deleted"}), 200


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
