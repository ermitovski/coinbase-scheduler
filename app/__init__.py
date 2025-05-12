import os
from flask import Flask
from app.scheduler import init_scheduler
from dotenv import load_dotenv

def create_app():
    # Load environment variables
    load_dotenv()
    
    # Initialize Flask app
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default-dev-key')
    
    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    # Initialize scheduler for daily buys
    init_scheduler()
    
    return app
