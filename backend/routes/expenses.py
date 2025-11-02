from flask import Blueprint, request, jsonify
from models.expense import Expense
from models.group import Group
from utils.auth import require_auth

expenses_bp = Blueprint('expenses', __name__)

# In backend/routes/expenses.py

@expenses_bp.route('', methods=['POST'])
@require_auth
def create_expense(current_user_id):
    try:
        data = request.get_json()
        description = data.get('description')
        amount = data.get('amount')
        group_id = data.get('groupId')
        participant_ids = data.get('participantIds', [])
        
        # --- ADD THESE DEBUG LINES ---
        print("\n--- DEBUG: create_expense ROUTE ---")
        print(f"Payer ID: {current_user_id}")
        print(f"Group ID: {group_id}")
        print(f"Participant IDs Received: {participant_ids}")
        print(f"Amount: {amount}")
        print("---------------------------------------\n")
        # ---------------------------------

        # Validation
        if not description or not amount or not group_id or not participant_ids:
            return jsonify({"error": "Missing required fields"}), 400
        
        # Verify user is a member of the group
        if not Group.is_member(group_id, current_user_id):
            return jsonify({"error": "Forbidden"}), 403
        
        # Create expense (current user is the payer)
        expense = Expense.create(
            description=description,
            amount=amount,
            group_id=group_id,
            paid_by_id=current_user_id,
            participant_ids=participant_ids
        )
        
        # --- ADD THIS DEBUG LINE ---
        print(f"Expense.create returned: {expense}")
        # ---------------------------

        if not expense:
            return jsonify({"error": "Failed to create expense"}), 500
        
        return jsonify(expense), 201
        
    except Exception as e:
        print(f"Create expense error: {e}")
        return jsonify({"error": "Failed to create expense"}), 500
    
@expenses_bp.route('/<expense_id>', methods=['GET'])
@require_auth
def get_expense(expense_id, current_user_id):
    """Get expense details"""
    try:
        expense = Expense.find_by_id(expense_id)
        
        if not expense:
            return jsonify({"error": "Expense not found"}), 404
        
        # Verify user is a member of the group
        if not Group.is_member(expense['groupId'], current_user_id):
            return jsonify({"error": "Forbidden"}), 403
        
        return jsonify(expense), 200
        
    except Exception as e:
        print(f"Get expense error: {e}")
        return jsonify({"error": "Failed to retrieve expense"}), 500

@expenses_bp.route('/<expense_id>', methods=['DELETE'])
@require_auth
def delete_expense(expense_id, current_user_id):
    """Delete an expense"""
    try:
        success = Expense.delete(expense_id, current_user_id)
        
        if not success:
            return jsonify({"error": "Forbidden or Not Found"}), 403
        
        return jsonify({"message": "Expense deleted successfully"}), 200
        
    except Exception as e:
        print(f"Delete expense error: {e}")
        return jsonify({"error": "Failed to delete expense"}), 500

@expenses_bp.route('/group/<group_id>', methods=['GET'])
@require_auth
def get_group_expenses(group_id, current_user_id):
    """Get all expenses for a group"""
    try:
        # Verify user is a member
        if not Group.is_member(group_id, current_user_id):
            return jsonify({"error": "Forbidden"}), 403
        
        expenses = Expense.get_all_for_group(group_id)
        return jsonify(expenses), 200
        
    except Exception as e:
        print(f"Get group expenses error: {e}")
        return jsonify({"error": "Failed to retrieve expenses"}), 500

@expenses_bp.route('/user', methods=['GET'])
@require_auth
def get_user_expenses(current_user_id):
    """Get all expenses the current user is involved in"""
    try:
        expenses = Expense.get_user_expenses(current_user_id)
        return jsonify(expenses), 200
        
    except Exception as e:
        print(f"Get user expenses error: {e}")
        return jsonify({"error": "Failed to retrieve expenses"}), 500