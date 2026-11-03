from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

import os

load_dotenv()


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

    CORS(app)

    @app.route("/")
    def home():
        return {
            "application": "MaintainAI",
            "message": "Backend is running",
            "status": "success"
        }

    @app.route("/api/health")
    def health():
        return {
            "status": "healthy",
            "application": "MaintainAI"
        }

    return app