from flask import Blueprint, request, jsonify
from models.settlement import Settlement
from models.group import Group
from models.expense import Expense
from utils.auth import require_auth
from utils.calculations import calculate_balances, settle_debts

settlements_bp = Blueprint('settlements', __name__)

@settlements_bp.route('', methods=['POST'])
@require_auth
def create_settlement(current_user_id):
    """Record a settlement payment"""
    try:
        data = request.get_json()
        group_id = data.get('groupId')
        to_user_id = data.get('toUserId')
        amount = data.get('amount')
        
        # Validation
        if not group_id or not to_user_id or not amount:
            return jsonify({"error": "Missing required fields"}), 400
        
        # Verify user is a member of the group
        if not Group.is_member(group_id, current_user_id):
            return jsonify({"error": "Forbidden"}), 403
        
        # Create settlement (current user is paying)
        settlement = Settlement.create(
            group_id=group_id,
            from_user_id=current_user_id,
            to_user_id=to_user_id,
            amount=amount
        )
        
        if not settlement:
            return jsonify({"error": "Failed to record settlement"}), 500
        
        return jsonify(settlement), 201
        
    except Exception as e:
        print(f"Create settlement error: {e}")
        return jsonify({"error": "Failed to record settlement"}), 500

@settlements_bp.route('/group/<group_id>', methods=['GET'])
@require_auth
def get_group_settlements(group_id, current_user_id):
    """Get all settlements for a group"""
    try:
        # Verify user is a member
        if not Group.is_member(group_id, current_user_id):
            return jsonify({"error": "Forbidden"}), 403
        
        settlements = Settlement.get_for_group(group_id)
        return jsonify(settlements), 200
        
    except Exception as e:
        print(f"Get settlements error: {e}")
        return jsonify({"error": "Failed to retrieve settlements"}), 500

@settlements_bp.route('/balances/group/<group_id>', methods=['GET'])
@require_auth
def get_group_balances(group_id, current_user_id):
    """Calculate and return balances and suggested payments for a group"""
    try:
        # Verify user is a member
        if not Group.is_member(group_id, current_user_id):
            return jsonify({"error": "Forbidden"}), 403
        
        # Get group details
        group = Group.get_with_details(group_id, current_user_id)
        if not group:
            return jsonify({"error": "Group not found"}), 404
        
        # Get settlements
        settlements = Settlement.get_for_group(group_id)
        
        # Calculate balances
        balances = calculate_balances(
            expenses=group['expenses'],
            members=group['members'],
            settlements=settlements
        )
        
        # Generate payment suggestions
        payments = settle_debts(balances)
        
        return jsonify({
            "balances": balances,
            "settlements": payments
        }), 200
        
    except Exception as e:
        print(f"Calculate balances error: {e}")
        return jsonify({"error": "Failed to calculate balances"}), 500

@settlements_bp.route('/balances', methods=['GET'])
@require_auth
def get_all_balances(current_user_id):
    """Get balances across all groups for the current user"""
    try:
        from models.user import User
        
        # Get all user's groups
        groups = User.get_groups(current_user_id)
        
        all_balances = {}
        all_settlements = []
        
        for group in groups:
            # Get group details
            group_details = Group.get_with_details(group['id'], current_user_id)
            if not group_details:
                continue
            
            # Get settlements
            settlements = Settlement.get_for_group(group['id'])
            
            # Calculate balances for this group
            balances = calculate_balances(
                expenses=group_details['expenses'],
                members=group_details['members'],
                settlements=settlements
            )
            
            # Generate payment suggestions
            payments = settle_debts(balances)
            
            # Add to overall results
            for user_id, balance in balances.items():
                if user_id not in all_balances:
                    all_balances[user_id] = 0.0
                all_balances[user_id] += balance
            
            # Add group info to settlements
            for payment in payments:
                payment['groupId'] = group['id']
                payment['groupName'] = group['name']
                all_settlements.append(payment)
        
        return jsonify({
            "balances": all_balances,
            "settlements": all_settlements
        }), 200
        
    except Exception as e:
        print(f"Calculate all balances error: {e}")
        return jsonify({"error": "Failed to calculate balances"}), 500