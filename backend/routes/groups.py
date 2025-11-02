from flask import Blueprint, request, jsonify
from models.group import Group
from models.user import User
from utils.auth import require_auth

groups_bp = Blueprint('groups', __name__)

@groups_bp.route('', methods=['POST'])
@require_auth
def create_group(current_user_id):
    """Create a new group"""
    try:
        data = request.get_json()
        name = data.get('name')
        
        if not name:
            return jsonify({"error": "Group name is required"}), 400
        
        group = Group.create(name, current_user_id)
        
        if not group:
            return jsonify({"error": "Failed to create group"}), 500
        
        return jsonify(group), 201
        
    except Exception as e:
        print(f"Create group error: {e}")
        return jsonify({"error": "Failed to create group"}), 500

@groups_bp.route('/<group_id>', methods=['GET'])
@require_auth
def get_group(group_id, current_user_id):
    """Get group details with members and expenses"""
    try:
        group = Group.get_with_details(group_id, current_user_id)
        
        if not group:
            return jsonify({"error": "Forbidden or Not Found"}), 403
        
        return jsonify(group), 200
        
    except Exception as e:
        print(f"Get group error: {e}")
        return jsonify({"error": "Failed to retrieve group"}), 500

@groups_bp.route('/<group_id>', methods=['DELETE'])
@require_auth
def delete_group(group_id, current_user_id):
    """Delete a group and all its data"""
    try:
        success = Group.delete(group_id, current_user_id)
        
        if not success:
            return jsonify({"error": "Forbidden or Not Found"}), 403
        
        return jsonify({"message": "Group deleted successfully"}), 200
        
    except Exception as e:
        print(f"Delete group error: {e}")
        return jsonify({"error": "Failed to delete group"}), 500

@groups_bp.route('/<group_id>/members', methods=['POST'])
@require_auth
def add_member(group_id, current_user_id):
    """Add a new member to the group"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({"error": "Email is required"}), 400
        
        user_to_add = User.find_by_email(email)
        if not user_to_add:
            return jsonify({"error": "User with that email not found."}), 404
        
        if not Group.is_member(group_id, current_user_id):
            return jsonify({"error": "Forbidden: You are not a member of this group."}), 403
        
        success = Group.add_member(group_id, email, current_user_id)
        
        if not success:
            return jsonify({"error": "User is already a member of this group."}), 409
        
        return jsonify({"message": "User added successfully!"}), 200
        
    except Exception as e:
        print(f"Add member error: {e}")
        return jsonify({"error": "Failed to add member"}), 500

@groups_bp.route('/user', methods=['GET'])
@require_auth
def get_user_groups(current_user_id):
    """Get all groups the current user is a member of"""
    try:
        groups = User.get_groups(current_user_id)
        return jsonify(groups), 200
        
    except Exception as e:
        print(f"Get user groups error: {e}")
        return jsonify({"error": "Failed to retrieve groups"}), 500
