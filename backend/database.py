from neo4j import GraphDatabase
from flask import g
from config import Config

# Validate configuration on import
Config.validate()

# Create the driver (singleton)
driver = GraphDatabase.driver(
    Config.NEO4J_URI,
    auth=(Config.NEO4J_USERNAME, Config.NEO4J_PASSWORD),
    max_connection_lifetime=3600,
    max_connection_pool_size=50,
    connection_acquisition_timeout=120
)

def get_db():
    """Get database session from Flask's g object or create new one"""
    if 'db' not in g:
        g.db = driver.session(database=Config.NEO4J_DATABASE)
    return g.db

def close_db(e=None):
    """Close database session"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize database with constraints and indexes"""
    with driver.session(database=Config.NEO4J_DATABASE) as session:
        # Create uniqueness constraints (automatically creates indexes)
        constraints = [
            "CREATE CONSTRAINT user_id_unique IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE",
            "CREATE CONSTRAINT user_email_unique IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE",
            "CREATE CONSTRAINT group_id_unique IF NOT EXISTS FOR (g:Group) REQUIRE g.id IS UNIQUE",
            "CREATE CONSTRAINT expense_id_unique IF NOT EXISTS FOR (e:Expense) REQUIRE e.id IS UNIQUE",
            "CREATE CONSTRAINT settlement_id_unique IF NOT EXISTS FOR (s:Settlement) REQUIRE s.id IS UNIQUE",
        ]
        
        for constraint in constraints:
            try:
                session.run(constraint)
                print(f"✓ Created: {constraint.split('FOR')[1].split('REQUIRE')[0].strip()}")
            except Exception as e:
                if "EquivalentSchemaRuleAlreadyExists" not in str(e):
                    print(f"✗ Error creating constraint: {e}")
        
        # Create additional indexes for performance
        indexes = [
            "CREATE INDEX user_name_idx IF NOT EXISTS FOR (u:User) ON (u.name)",
            "CREATE INDEX expense_created_idx IF NOT EXISTS FOR (e:Expense) ON (e.createdAt)",
            "CREATE INDEX settlement_paid_idx IF NOT EXISTS FOR (s:Settlement) ON (s.paidAt)",
        ]
        
        for index in indexes:
            try:
                session.run(index)
                print(f"✓ Created: {index.split('FOR')[1].split('ON')[0].strip()}")
            except Exception as e:
                if "EquivalentSchemaRuleAlreadyExists" not in str(e):
                    print(f"✗ Error creating index: {e}")
        
        print("\n✅ Database initialization complete!")

def close_driver():
    """Close the driver connection (called on application shutdown)"""
    driver.close()
