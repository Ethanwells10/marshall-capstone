from flask import Flask, jsonify
from datetime import datetime, timezone


def create_app():
    app = Flask(__name__)

    @app.route("/")
    def index():
        return "<h1>Market Monitor</h1><p>Coming soon.</p>"

    @app.route("/api/health")
    def health():
        return jsonify({
            "status": "ok",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    return app
