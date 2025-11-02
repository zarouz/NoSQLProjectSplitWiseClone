import uuid
from database import get_db

class User:
    @staticmethod
    def create(email, name, hashed_password):
        """Create a new user node in Neo4j"""
        db = get_db()
        user_id = str(uuid.uuid4())
        
        query = """
        CREATE (u:User {
            id: $id,
            email: $email,
            name: $name,
            hashedPassword: $hashedPassword,
            createdAt: datetime()
        })
        RETURN u
        """
        
        result = db.run(query, 
                       id=user_id, 
                       email=email, 
                       name=name, 
                       hashedPassword=hashed_password)
        
        record = result.single()
        if record:
            user_node = record['u']
            return {
                'id': user_node['id'],
                'email': user_node['email'],
                'name': user_node['name']
            }
        return None
    
    @staticmethod
    def find_by_email(email):
        """Find user by email"""
        db = get_db()
        
        query = """
        MATCH (u:User {email: $email})
        RETURN u
        """
        
        result = db.run(query, email=email)
        record = result.single()
        
        if record:
            user_node = record['u']
            return {
                'id': user_node['id'],
                'email': user_node['email'],
                'name': user_node['name'],
                'hashedPassword': user_node.get('hashedPassword')
            }
        return None
    
    @staticmethod
    def find_by_id(user_id):
        """Find user by ID"""
        db = get_db()
        
        query = """
        MATCH (u:User {id: $id})
        RETURN u
        """
        
        result = db.run(query, id=user_id)
        record = result.single()
        
        if record:
            user_node = record['u']
            return {
                'id': user_node['id'],
                'email': user_node['email'],
                'name': user_node['name']
            }
        return None
    
    @staticmethod
    def exists_by_email(email):
        """Check if user exists by email"""
        db = get_db()
        
        query = """
        MATCH (u:User {email: $email})
        RETURN count(u) > 0 as exists
        """
        
        result = db.run(query, email=email)
        record = result.single()
        return record['exists'] if record else False
    
    @staticmethod
    def get_all():
        """Get all users"""
        db = get_db()
        
        query = """
        MATCH (u:User)
        RETURN u
        ORDER BY u.name
        """
        
        result = db.run(query)
        users = []
        
        for record in result:
            user_node = record['u']
            users.append({
                'id': user_node['id'],
                'email': user_node['email'],
                'name': user_node['name']
            })
        
        return users
    
    @staticmethod
    def get_groups(user_id):
        """Get all groups a user is a member of"""
        db = get_db()
        
        query = """
        MATCH (u:User {id: $userId})-[:MEMBER_OF]->(g:Group)
        OPTIONAL MATCH (g)<-[:MEMBER_OF]-(member:User)
        WITH g, count(DISTINCT member) as memberCount
        RETURN g, memberCount
        ORDER BY g.name
        """
        
        result = db.run(query, userId=user_id)
        groups = []
        
        for record in result:
            group_node = record['g']
            groups.append({
                'id': group_node['id'],
                'name': group_node['name'],
                '_count': {
                    'members': record['memberCount']
                }
            })
        
        return groups
