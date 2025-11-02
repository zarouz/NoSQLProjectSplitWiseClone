#!/usr/bin/env python3
"""
Test script to verify Neo4j connection and basic operations
Run this after setting up your .env file
"""

import sys
from database import driver, init_db
from config import Config

def test_connection():
    """Test Neo4j connection"""
    print("🔍 Testing Neo4j connection...")
    try:
        # Verify the driver can connect
        driver.verify_connectivity()
        print("✅ Successfully connected to Neo4j!")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check your .env file has correct credentials")
        print("2. Verify NEO4J_URI format: neo4j+s://xxxxx.databases.neo4j.io")
        print("3. Ensure your IP is whitelisted in Neo4j Aura")
        return False

def test_constraints():
    """Test database constraints"""
    print("\n🔍 Testing database constraints...")
    try:
        init_db()
        print("✅ Database constraints and indexes created successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to create constraints: {e}")
        return False

def test_basic_operations():
    """Test basic CRUD operations"""
    print("\n🔍 Testing basic CRUD operations...")
    try:
        with driver.session(database=Config.NEO4J_DATABASE) as session:
            # Create a test user
            result = session.run("""
                CREATE (u:TestUser {id: 'test-123', name: 'Test User'})
                RETURN u
            """)
            record = result.single()
            if record:
                print("✅ Create operation successful")
            
            # Read the test user
            result = session.run("""
                MATCH (u:TestUser {id: 'test-123'})
                RETURN u
            """)
            record = result.single()
            if record:
                print("✅ Read operation successful")
            
            # Update the test user
            result = session.run("""
                MATCH (u:TestUser {id: 'test-123'})
                SET u.name = 'Updated Test User'
                RETURN u
            """)
            record = result.single()
            if record:
                print("✅ Update operation successful")
            
            # Delete the test user
            result = session.run("""
                MATCH (u:TestUser {id: 'test-123'})
                DELETE u
                RETURN count(u) as deleted
            """)
            record = result.single()
            if record and record['deleted'] > 0:
                print("✅ Delete operation successful")
            
            return True
    except Exception as e:
        print(f"❌ CRUD operations failed: {e}")
        return False

def test_graph_queries():
    """Test graph-specific queries"""
    print("\n🔍 Testing graph queries...")
    try:
        with driver.session(database=Config.NEO4J_DATABASE) as session:
            # Create test data
            session.run("""
                CREATE (u1:TestUser {id: '1', name: 'Alice'})
                CREATE (u2:TestUser {id: '2', name: 'Bob'})
                CREATE (g:TestGroup {id: 'g1', name: 'Test Group'})
                CREATE (u1)-[:TEST_MEMBER_OF]->(g)
                CREATE (u2)-[:TEST_MEMBER_OF]->(g)
            """)
            print("✅ Test graph structure created")
            
            # Test relationship query
            result = session.run("""
                MATCH (u:TestUser)-[:TEST_MEMBER_OF]->(g:TestGroup)
                RETURN count(u) as memberCount
            """)
            record = result.single()
            if record and record['memberCount'] == 2:
                print("✅ Relationship query successful")
            
            # Test pattern matching
            result = session.run("""
                MATCH (u1:TestUser {id: '1'})-[:TEST_MEMBER_OF]->(g:TestGroup)
                      <-[:TEST_MEMBER_OF]-(u2:TestUser)
                WHERE u1 <> u2
                RETURN u2.name as coMember
            """)
            record = result.single()
            if record and record['coMember'] == 'Bob':
                print("✅ Pattern matching successful")
            
            # Cleanup
            session.run("""
                MATCH (n:TestUser) DETACH DELETE n
            """)
            session.run("""
                MATCH (n:TestGroup) DETACH DELETE n
            """)
            print("✅ Test data cleaned up")
            
            return True
    except Exception as e:
        print(f"❌ Graph queries failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Neo4j Expense Splitter - Database Test Suite")
    print("=" * 60)
    
    # Test configuration
    try:
        Config.validate()
        print("✅ Configuration validated")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\nPlease create a .env file with your Neo4j credentials")
        sys.exit(1)
    
    # Run tests
    all_passed = True
    all_passed &= test_connection()
    
    if all_passed:
        all_passed &= test_constraints()
        all_passed &= test_basic_operations()
        all_passed &= test_graph_queries()
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All tests passed! Your Neo4j setup is ready.")
        print("\nYou can now run: python app.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    print("=" * 60)
    
    # Close driver
    driver.close()
    sys.exit(0 if all_passed else 1)

if __name__ == '__main__':
    main()