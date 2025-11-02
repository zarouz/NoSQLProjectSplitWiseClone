from flask import Blueprint, request, jsonify
import re
from models.user import User
from utils.auth import hash_password, verify_password, generate_token

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password complexity"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number."
    return True, None

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        email = data.get('email')
        name = data.get('name')
        password = data.get('password')
        
        if not email or not name or not password:
            return jsonify({"error": "Missing required fields"}), 400
        
        if not validate_email(email):
            return jsonify({"error": "Please enter a valid email address."}), 400
        
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        
        if User.exists_by_email(email):
            return jsonify({"error": "User with this email already exists."}), 409
        
        hashed_password = hash_password(password)
        user = User.create(email, name, hashed_password)
        
        if not user:
            return jsonify({"error": "Failed to create user"}), 500
        
        return jsonify({
            "message": "User created successfully",
            "user": {
                "id": user['id'],
                "email": user['email'],
                "name": user['name']
            }
        }), 201
        
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({"error": "Invalid credentials"}), 401
        
        user = User.find_by_email(email)
        if not user or not user.get('hashedPassword'):
            return jsonify({"error": "Invalid credentials"}), 401
        
        if not verify_password(password, user['hashedPassword']):
            return jsonify({"error": "Invalid credentials"}), 401
        
        token = generate_token(user['id'])
        
        return jsonify({
            "token": token,
            "user": {
                "id": user['id'],
                "email": user['email'],
                "name": user['name']
            }
        }), 200
        
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@auth_bp.route('/session', methods=['GET'])
def get_session():
    """Get current user session"""
    from utils.auth import get_current_user
    
    try:
        user_id = get_current_user()
        if not user_id:
            return jsonify({"user": None}), 200
        
        user = User.find_by_id(user_id)
        if not user:
            return jsonify({"user": None}), 200
        
        return jsonify({
            "user": {
                "id": user['id'],
                "email": user['email'],
                "name": user['name']
            }
        }), 200
        
    except Exception as e:
        print(f"Session error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
