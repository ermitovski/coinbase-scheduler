import os
from flask import Flask
from app.scheduler import init_scheduler
from dotenv import load_dotenv

def create_app(init_sched=False):
    # Load environment variables
    load_dotenv()
    
    # Initialize Flask app
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default-dev-key')
    
    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    # Only initialize scheduler if explicitly requested
    # (it will run in a separate process in production)
    if init_sched:
        init_scheduler()
    
    return app
