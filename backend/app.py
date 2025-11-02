from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from routes.auth import auth_bp
from routes.groups import groups_bp
from routes.expenses import expenses_bp
from routes.settlements import settlements_bp
from database import init_db, close_db

app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS for Next.js frontend
CORS(app, 
     origins=["http://localhost:3000"],
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Initialize database constraints and indexes
with app.app_context():
    init_db()

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(groups_bp, url_prefix='/api/groups')
app.register_blueprint(expenses_bp, url_prefix='/api/expenses')
app.register_blueprint(settlements_bp, url_prefix='/api/settlements')

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "database": "neo4j"}), 200

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# Cleanup on shutdown
@app.teardown_appcontext
def shutdown_session(exception=None):
    close_db()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
