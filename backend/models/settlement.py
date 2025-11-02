import uuid
from database import get_db
from datetime import datetime

class Settlement:
    @staticmethod
    def create(group_id, from_user_id, to_user_id, amount):
        """Record a settlement payment between two users in a group"""
        db = get_db()
        settlement_id = str(uuid.uuid4())
        
        query = """
        // Verify both users are members of the group
        MATCH (fromUser:User {id: $fromUserId})-[:MEMBER_OF]->(g:Group {id: $groupId})
        MATCH (toUser:User {id: $toUserId})-[:MEMBER_OF]->(g)
        
        // Create settlement node
        CREATE (s:Settlement {
            id: $settlementId,
            amount: $amount,
            paidAt: datetime()
        })
        
        // Link settlement to group and users
        CREATE (s)-[:IN_GROUP]->(g)
        CREATE (s)-[:FROM]->(fromUser)
        CREATE (s)-[:TO]->(toUser)
        
        RETURN s
        """
        
        result = db.run(query,
                       settlementId=settlement_id,
                       groupId=group_id,
                       fromUserId=from_user_id,
                       toUserId=to_user_id,
                       amount=float(amount))
        
        record = result.single()
        if record:
            settlement_node = record['s']
            return {
                'id': settlement_node['id'],
                'amount': settlement_node['amount'],
                'paidAt': settlement_node['paidAt'].isoformat() if hasattr(settlement_node['paidAt'], 'isoformat') else str(settlement_node['paidAt']),
                'groupId': group_id,
                'fromUserId': from_user_id,
                'toUserId': to_user_id
            }
        return None
    
    @staticmethod
    def get_for_group(group_id):
        """Get all settlements for a group"""
        db = get_db()
        
        query = """
        MATCH (s:Settlement)-[:IN_GROUP]->(g:Group {id: $groupId})
        MATCH (s)-[:FROM]->(fromUser:User)
        MATCH (s)-[:TO]->(toUser:User)
        
        RETURN s, fromUser, toUser
        ORDER BY s.paidAt DESC
        """
        
        result = db.run(query, groupId=group_id)
        settlements = []
        
        for record in result:
            settlement_node = record['s']
            from_user = record['fromUser']
            to_user = record['toUser']
            
            settlements.append({
                'id': settlement_node['id'],
                'amount': settlement_node['amount'],
                'paidAt': settlement_node['paidAt'].isoformat() if hasattr(settlement_node['paidAt'], 'isoformat') else str(settlement_node['paidAt']),
                'groupId': group_id,
                'fromUserId': from_user['id'],
                'fromUser': {
                    'id': from_user['id'],
                    'name': from_user['name']
                },
                'toUserId': to_user['id'],
                'toUser': {
                    'id': to_user['id'],
                    'name': to_user['name']
                }
            })
        
        return settlements
    
    @staticmethod
    def get_between_users(group_id, from_user_id, to_user_id):
        """Get all settlements from one user to another in a group"""
        db = get_db()
        
        query = """
        MATCH (s:Settlement)-[:IN_GROUP]->(g:Group {id: $groupId})
        MATCH (s)-[:FROM]->(fromUser:User {id: $fromUserId})
        MATCH (s)-[:TO]->(toUser:User {id: $toUserId})
        
        RETURN s
        ORDER BY s.paidAt DESC
        """
        
        result = db.run(query, 
                       groupId=group_id,
                       fromUserId=from_user_id,
                       toUserId=to_user_id)
        
        settlements = []
        for record in result:
            settlement_node = record['s']
            settlements.append({
                'id': settlement_node['id'],
                'amount': settlement_node['amount'],
                'paidAt': settlement_node['paidAt'].isoformat() if hasattr(settlement_node['paidAt'], 'isoformat') else str(settlement_node['paidAt']),
                'fromUserId': from_user_id,
                'toUserId': to_user_id
            })
        
        return settlements
    
    @staticmethod
    def get_total_paid(group_id, from_user_id, to_user_id):
        """Get total amount paid from one user to another in a group"""
        db = get_db()
        
        query = """
        MATCH (s:Settlement)-[:IN_GROUP]->(g:Group {id: $groupId})
        MATCH (s)-[:FROM]->(:User {id: $fromUserId})
        MATCH (s)-[:TO]->(:User {id: $toUserId})
        
        RETURN COALESCE(sum(s.amount), 0) as totalPaid
        """
        
        result = db.run(query,
                       groupId=group_id,
                       fromUserId=from_user_id,
                       toUserId=to_user_id)
        
        record = result.single()
        return record['totalPaid'] if record else 0.0
    
    @staticmethod
    def delete_for_group(group_id):
        """Delete all settlements for a group"""
        db = get_db()
        
        query = """
        MATCH (s:Settlement)-[:IN_GROUP]->(g:Group {id: $groupId})
        DETACH DELETE s
        RETURN count(s) as deleted
        """
        
        result = db.run(query, groupId=group_id)
        record = result.single()
        return record['deleted'] if record else 0