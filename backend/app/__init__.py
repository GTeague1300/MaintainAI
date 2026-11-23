import os

from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from sqlalchemy import text
from app.routes.equipment import equipment_bp
from app.extensions import db, migrate
from app.models import User, Equipment, MaintenanceRequest
from app.routes.maintenance_requests import maintenance_requests_bp

load_dotenv()


def create_app(test_config=None):

    app = Flask(__name__)

    database_url = os.getenv("DATABASE_URL")

    if database_url and database_url.startswith("postgresql://"):
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

    if test_config:
        app.config.update(test_config)

    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        raise RuntimeError("DATABASE_URL is not configured.")

    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True
    }

    # Initialise database extensions HERE
    db.init_app(app)
    migrate.init_app(app, db)

    CORS(app)

    app.register_blueprint(
        equipment_bp,
        url_prefix="/api/equipment"
)
    app.register_blueprint(
    maintenance_requests_bp,
    url_prefix="/api/maintenance-requests"
)

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