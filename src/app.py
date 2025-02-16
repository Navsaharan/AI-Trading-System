from flask import Flask, render_template
from flask_cors import CORS
from src.routes.admin_routes import admin
from src.routes.user_routes import user
from src.routes.auth_routes import auth
from src.routes.api_routes import api
from src.config.settings import Settings
import os
from dotenv import load_dotenv

# Project name
PROJECT_NAME = 'FamilyHVSDN'

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__,
    template_folder='frontend/templates',
    static_folder='frontend/static'
)

# Enable CORS
CORS(app)

# Load configuration
app.config.from_object(Settings)

# Register blueprints
app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(user, url_prefix='/user')
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(api, url_prefix='/api')

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
