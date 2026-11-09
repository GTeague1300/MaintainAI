import os

from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from sqlalchemy import text

from app.extensions import db, migrate
from app.models import User, Equipment, MaintenanceRequest

load_dotenv()


def create_app():

    app = Flask(__name__)

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured.")

    if database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True
    }

    # Initialise database extensions HERE
    db.init_app(app)
    migrate.init_app(app, db)

    CORS(app)

    @app.route("/")
    def home():
        return jsonify({
            "application": "MaintainAI",
            "message": "Backend is running",
            "status": "success"
        })

    @app.route("/api/health")
    def health():
        return jsonify({
            "status": "healthy",
            "application": "MaintainAI"
        })

    @app.route("/api/health/database")
    def database_health():
        try:
            db.session.execute(text("SELECT 1"))

            return jsonify({
                "database": "connected",
                "status": "success"
            })

        except Exception:
            db.session.rollback()

            return jsonify({
                "database": "unavailable",
                "status": "error"
            }), 503

    return app