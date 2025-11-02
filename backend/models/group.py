import uuid
from database import get_db

class Group:
    @staticmethod
    def create(name, creator_id):
        """Create a new group and add creator as first member"""
        db = get_db()
        group_id = str(uuid.uuid4())
        
        query = """
        MATCH (u:User {id: $creatorId})
        CREATE (g:Group {
            id: $groupId,
            name: $name,
            createdAt: datetime()
        })
        CREATE (u)-[:MEMBER_OF]->(g)
        RETURN g
        """
        
        result = db.run(query, 
                       groupId=group_id,
                       name=name,
                       creatorId=creator_id)
        
        record = result.single()
        if record:
            group_node = record['g']
            return {
                'id': group_node['id'],
                'name': group_node['name']
            }
        return None
    
    @staticmethod
    def find_by_id(group_id, user_id=None):
        """Find group by ID, optionally verify user is a member"""
        db = get_db()
        
        if user_id:
            query = """
            MATCH (u:User {id: $userId})-[:MEMBER_OF]->(g:Group {id: $groupId})
            RETURN g
            """
            result = db.run(query, groupId=group_id, userId=user_id)
        else:
            query = """
            MATCH (g:Group {id: $groupId})
            RETURN g
            """
            result = db.run(query, groupId=group_id)
        
        record = result.single()
        if record:
            group_node = record['g']
            return {
                'id': group_node['id'],
                'name': group_node['name']
            }
        return None
    
    @staticmethod
    def get_with_details(group_id, user_id):
        """Get group with members and expenses"""
        db = get_db()
        
        query = """
        MATCH (u:User {id: $userId})-[:MEMBER_OF]->(g:Group {id: $groupId})
        
        // Collect members first
        OPTIONAL MATCH (g)<-[:MEMBER_OF]-(member:User)
        WITH g, collect(DISTINCT {
            id: member.id, 
            name: member.name, 
            email: member.email
        }) as members
        
        // Find all expenses for the group
        OPTIONAL MATCH (g)<-[:BELONGS_TO]-(expense:Expense)
        
        // For each expense, find the payer and participants
        OPTIONAL MATCH (expense)<-[:PAID]-(paidBy:User)
        OPTIONAL MATCH (expense)<-[:PARTICIPANT_IN]-(participant:User)
        
        // Pre-aggregate participants for EACH expense
        WITH g, members, expense, paidBy, collect(DISTINCT participant) as participants
        
        // Now, collect all expense data (this is NOT nested)
        WITH g, members, collect(DISTINCT {
            expense: expense,
            paidBy: paidBy,
            participants: participants
        }) as expenseData
        
        RETURN g, members, expenseData
        """
        
        result = db.run(query, groupId=group_id, userId=user_id)
        record = result.single()
        
        if not record:
            return None
        
        group_node = record['g']
        members = [m for m in record['members'] if m['id'] is not None]
        
        expenses = []
        for exp_data in record['expenseData']:
            expense = exp_data['expense']
            if expense is None:
                continue
                
            paidBy = exp_data['paidBy']
            participants = [p for p in exp_data['participants'] if p is not None]
            
            expenses.append({
                'id': expense['id'],
                'description': expense['description'],
                'amount': expense['amount'],
                'createdAt': expense['createdAt'].isoformat() if hasattr(expense['createdAt'], 'isoformat') else str(expense['createdAt']),
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
        
        expenses.sort(key=lambda x: x['createdAt'], reverse=True)
        
        return {
            'id': group_node['id'],
            'name': group_node['name'],
            'members': members,
            'expenses': expenses
        }
    
    @staticmethod
    def add_member(group_id, user_email, current_user_id):
        """Add a new member to the group"""
        db = get_db()
        
        query = """
        MATCH (currentUser:User {id: $currentUserId})-[:MEMBER_OF]->(g:Group {id: $groupId})
        MATCH (newUser:User {email: $userEmail})
        OPTIONAL MATCH (newUser)-[existingRel:MEMBER_OF]->(g)
        WITH g, newUser, existingRel
        WHERE existingRel IS NULL
        CREATE (newUser)-[:MEMBER_OF]->(g)
        RETURN newUser
        """
        
        result = db.run(query, 
                       groupId=group_id,
                       userEmail=user_email,
                       currentUserId=current_user_id)
        
        record = result.single()
        return record is not None
    
    @staticmethod
    def is_member(group_id, user_id):
        """Check if user is a member of the group"""
        db = get_db()
        
        query = """
        MATCH (u:User {id: $userId})-[:MEMBER_OF]->(g:Group {id: $groupId})
        RETURN count(u) > 0 as isMember
        """
        
        result = db.run(query, groupId=group_id, userId=user_id)
        record = result.single()
        return record['isMember'] if record else False
    
    @staticmethod
    def delete(group_id, user_id):
        """Delete a group and all related data"""
        db = get_db()
        
        query = """
        MATCH (u:User {id: $userId})-[:MEMBER_OF]->(g:Group {id: $groupId})
        OPTIONAL MATCH (g)<-[:IN_GROUP]-(s:Settlement)
        DETACH DELETE s
        WITH g
        OPTIONAL MATCH (g)<-[:BELONGS_TO]-(e:Expense)
        DETACH DELETE e
        WITH g
        DETACH DELETE g
        RETURN count(g) as deleted
        """
        
        result = db.run(query, groupId=group_id, userId=user_id)
        record = result.single()
        return record['deleted'] > 0 if record else False
