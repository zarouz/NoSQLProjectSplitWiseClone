import uuid
from database import get_db
from datetime import datetime

class Expense:
    @staticmethod
    def create(description, amount, group_id, paid_by_id, participant_ids):
        """Create a new expense in a group"""
        db = get_db()
        expense_id = str(uuid.uuid4())
        
        query = """
        // Verify payer is a member of the group
        MATCH (payer:User {id: $paidById})-[:MEMBER_OF]->(g:Group {id: $groupId})
        
        // Create the expense
        CREATE (e:Expense {
            id: $expenseId,
            description: $description,
            amount: $amount,
            createdAt: datetime()
        })
        
        // Link expense to group and payer
        CREATE (e)-[:BELONGS_TO]->(g)
        CREATE (payer)-[:PAID]->(e)
        
        // Link all participants
        WITH e, g
        UNWIND $participantIds as participantId
        MATCH (participant:User {id: participantId})-[:MEMBER_OF]->(g)
        CREATE (participant)-[:PARTICIPANT_IN]->(e)
        
        // ADD THIS LINE
        WITH DISTINCT e
        
        RETURN e
        """
        
        result = db.run(query,
                       expenseId=expense_id,
                       description=description,
                       amount=float(amount),
                       groupId=group_id,
                       paidById=paid_by_id,
                       participantIds=participant_ids)
        
        record = result.single()
        if record:
            expense_node = record['e']
            return {
                'id': expense_node['id'],
                'description': expense_node['description'],
                'amount': expense_node['amount'],
                'createdAt': expense_node['createdAt'].isoformat() if hasattr(expense_node['createdAt'], 'isoformat') else str(expense_node['createdAt'])
            }
        return None
    
    @staticmethod
    def find_by_id(expense_id):
        """Find expense by ID with all details"""
        db = get_db()
        
        query = """
        MATCH (e:Expense {id: $expenseId})
        OPTIONAL MATCH (e)<-[:PAID]-(paidBy:User)
        OPTIONAL MATCH (e)<-[:PARTICIPANT_IN]-(participant:User)
        OPTIONAL MATCH (e)-[:BELONGS_TO]->(g:Group)
        
        RETURN e, paidBy, collect(DISTINCT participant) as participants, g
        """
        
        result = db.run(query, expenseId=expense_id)
        record = result.single()
        
        if not record:
            return None
        
        expense_node = record['e']
        paidBy = record['paidBy']
        participants = [p for p in record['participants'] if p is not None]
        group = record['g']
        
        return {
            'id': expense_node['id'],
            'description': expense_node['description'],
            'amount': expense_node['amount'],
            'createdAt': expense_node['createdAt'].isoformat() if hasattr(expense_node['createdAt'], 'isoformat') else str(expense_node['createdAt']),
            'paidById': paidBy['id'] if paidBy else None,
            'paidBy': {
                'id': paidBy['id'],
                'name': paidBy['name'],
                'email': paidBy['email']
            } if paidBy else None,
            'participants': [{
                'id': p['id'],
                'name': p['name'],
                'email': p['email']
            } for p in participants],
            'groupId': group['id'] if group else None
        }
    
    @staticmethod
    def get_all_for_group(group_id):
        """Get all expenses for a group"""
        db = get_db()
        
        query = """
        MATCH (g:Group {id: $groupId})<-[:BELONGS_TO]-(e:Expense)
        OPTIONAL MATCH (e)<-[:PAID]-(paidBy:User)
        OPTIONAL MATCH (e)<-[:PARTICIPANT_IN]-(participant:User)
        
        WITH e, paidBy, collect(DISTINCT participant) as participants
        RETURN e, paidBy, participants
        ORDER BY e.createdAt DESC
        """
        
        result = db.run(query, groupId=group_id)
        expenses = []
        
        for record in result:
            expense_node = record['e']
            paidBy = record['paidBy']
            participants = [p for p in record['participants'] if p is not None]
            
            expenses.append({
                'id': expense_node['id'],
                'description': expense_node['description'],
                'amount': expense_node['amount'],
                'createdAt': expense_node['createdAt'].isoformat() if hasattr(expense_node['createdAt'], 'isoformat') else str(expense_node['createdAt']),
                'paidById': paidBy['id'] if paidBy else None,
                'paidBy': {
                    'id': paidBy['id'],
                    'name': paidBy['name'],
                    'email': paidBy['email']
                } if paidBy else None,
                'participants': [{
                    'id': p['id'],
                    'name': p['name'],
                    'email': p['email']
                } for p in participants]
            })
        
        return expenses
    
    @staticmethod
    def delete(expense_id, user_id):
        """Delete an expense (only if user is member of the group)"""
        db = get_db()
        
        query = """
        MATCH (u:User {id: $userId})-[:MEMBER_OF]->(g:Group)<-[:BELONGS_TO]-(e:Expense {id: $expenseId})
        DETACH DELETE e
        RETURN count(e) as deleted
        """
        
        result = db.run(query, expenseId=expense_id, userId=user_id)
        record = result.single()
        return record['deleted'] > 0 if record else False
    
    @staticmethod
    def get_user_expenses(user_id):
        """Get all expenses a user is involved in (paid or participated)"""
        db = get_db()
        
        query = """
        MATCH (u:User {id: $userId})
        MATCH (e:Expense)
        WHERE (u)-[:PAID]->(e) OR (u)-[:PARTICIPANT_IN]->(e)
        
        OPTIONAL MATCH (e)<-[:PAID]-(paidBy:User)
        OPTIONAL MATCH (e)<-[:PARTICIPANT_IN]-(participant:User)
        OPTIONAL MATCH (e)-[:BELONGS_TO]->(g:Group)
        
        WITH e, paidBy, collect(DISTINCT participant) as participants, g
        RETURN e, paidBy, participants, g
        ORDER BY e.createdAt DESC
        """
        
        result = db.run(query, userId=user_id)
        expenses = []
        
        for record in result:
            expense_node = record['e']
            paidBy = record['paidBy']
            participants = [p for p in record['participants'] if p is not None]
            group = record['g']
            
            expenses.append({
                'id': expense_node['id'],
                'description': expense_node['description'],
                'amount': expense_node['amount'],
                'createdAt': expense_node['createdAt'].isoformat() if hasattr(expense_node['createdAt'], 'isoformat') else str(expense_node['createdAt']),
                'paidById': paidBy['id'] if paidBy else None,
                'paidBy': {
                    'id': paidBy['id'],
                    'name': paidBy['name']
                } if paidBy else None,
                'participants': [{
                    'id': p['id'],
                    'name': p['name']
                } for p in participants],
                'group': {
                    'id': group['id'],
                    'name': group['name']
                } if group else None
            })
        
        return expenses