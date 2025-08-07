import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()  # Load .env variables

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    print("Starting",flush=True)

    app.config.from_mapping(
        SECRET_KEY=os.getenv("FLASK_SECRET_KEY", "dev"),
        DATABASE=os.getenv("DATABASE", os.path.join(app.instance_path, 'tesla_tracker.db')),
        UPLOAD_FOLDER=os.getenv("UPLOAD_FOLDER", "uploads"),
        LATITUDE=float(os.getenv("LATITUDE")),
        LONGITUDE = float(os.getenv("LONGITUDE")),
        APP_USERNAME = os.getenv("APP_USERNAME"),
        APP_PASSWORD = os.getenv("APP_PASSWORD"),
        SYSTEM_KW=float(os.getenv('SYSTEM_KW', 6.2)),
        PERFORMANCE_RATIO = float(os.getenv('PERFORMANCE_RATIO', 0.60))
    )

    # Ensure instance and upload folders exist
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register blueprints
    from .routes.dashboard import dashboard_bp
    from .routes.bills import bills_bp
    from .routes.auth import auth_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(bills_bp)
    app.register_blueprint(auth_bp)



    return app
