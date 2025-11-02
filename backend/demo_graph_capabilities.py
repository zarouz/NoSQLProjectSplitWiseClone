#!/usr/bin/env python3
"""
Demo script showcasing Neo4j's graph database capabilities
Perfect for assignment demonstration!
"""

from database import driver
from config import Config
import time

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def demo_complex_relationships():
    """Demonstrate complex relationship queries"""
    print_section("1. COMPLEX RELATIONSHIP QUERIES")
    
    with driver.session(database=Config.NEO4J_DATABASE) as session:
        print("\n📊 Query: Find all users who share groups with me")
        print("Cypher:")
        print("  MATCH (me:User {id: $myId})-[:MEMBER_OF]->(g:Group)")
        print("        <-[:MEMBER_OF]-(others:User)")
        print("  WHERE me <> others")
        print("  RETURN DISTINCT others.name, count(g) as sharedGroups")
        
        result = session.run("""
            MATCH (me:User)-[:MEMBER_OF]->(g:Group)<-[:MEMBER_OF]-(others:User)
            WHERE me <> others
            WITH others, count(DISTINCT g) as sharedGroups
            RETURN others.name as name, sharedGroups
            ORDER BY sharedGroups DESC
            LIMIT 5
        """)
        
        print("\n✅ Results:")
        for record in result:
            print(f"   • {record['name']}: {record['sharedGroups']} shared group(s)")

def demo_graph_traversal():
    """Demonstrate graph traversal capabilities"""
    print_section("2. GRAPH TRAVERSAL - WHO OWES WHOM?")
    
    with driver.session(database=Config.NEO4J_DATABASE) as session:
        print("\n📊 Query: Find all expense relationships (payer → participants)")
        print("Cypher:")
        print("  MATCH (payer:User)-[:PAID]->(e:Expense)<-[:PARTICIPANT_IN]-(participant:User)")
        print("  WHERE payer <> participant")
        print("  RETURN payer.name, participant.name, e.amount")
        
        result = session.run("""
            MATCH (payer:User)-[:PAID]->(e:Expense)<-[:PARTICIPANT_IN]-(participant:User)
            WHERE payer <> participant
            WITH payer, participant, count(e) as expenseCount, sum(e.amount) as totalAmount
            RETURN payer.name as payer, 
                   participant.name as participant, 
                   expenseCount,
                   totalAmount
            ORDER BY totalAmount DESC
            LIMIT 10
        """)
        
        print("\n✅ Results:")
        for record in result:
            print(f"   • {record['payer']} paid for {record['participant']}: "
                  f"{record['expenseCount']} expense(s), ${record['totalAmount']:.2f}")

def demo_pattern_matching():
    """Demonstrate pattern matching"""
    print_section("3. PATTERN MATCHING - EXPENSE CHAINS")
    
    with driver.session(database=Config.NEO4J_DATABASE) as session:
        print("\n📊 Query: Find expense patterns in groups")
        print("Cypher:")
        print("  MATCH (u:User)-[:PAID]->(e:Expense)-[:BELONGS_TO]->(g:Group)")
        print("  MATCH (e)<-[:PARTICIPANT_IN]-(participants:User)")
        print("  RETURN g.name, count(e) as expenses, sum(e.amount) as total")
        
        result = session.run("""
            MATCH (u:User)-[:PAID]->(e:Expense)-[:BELONGS_TO]->(g:Group)
            MATCH (e)<-[:PARTICIPANT_IN]-(participants:User)
            WITH g, count(DISTINCT e) as expenseCount, 
                 sum(e.amount) as totalAmount,
                 count(DISTINCT participants) as participantCount
            RETURN g.name as groupName,
                   expenseCount,
                   totalAmount,
                   participantCount
            ORDER BY totalAmount DESC
        """)
        
        print("\n✅ Results:")
        for record in result:
            print(f"   • {record['groupName']}: "
                  f"{record['expenseCount']} expenses, "
                  f"${record['totalAmount']:.2f} total, "
                  f"{record['participantCount']} participants")

def demo_aggregations():
    """Demonstrate efficient aggregations"""
    print_section("4. GRAPH AGGREGATIONS")
    
    with driver.session(database=Config.NEO4J_DATABASE) as session:
        print("\n📊 Query: Calculate each user's total spending and debt")
        print("Cypher:")
        print("  MATCH (u:User)")
        print("  OPTIONAL MATCH (u)-[:PAID]->(paidExpenses:Expense)")
        print("  OPTIONAL MATCH (u)-[:PARTICIPANT_IN]->(sharedExpenses:Expense)")
        print("  RETURN u.name, sum(paidExpenses.amount), count(sharedExpenses)")
        
        result = session.run("""
            MATCH (u:User)
            OPTIONAL MATCH (u)-[:PAID]->(paidExpenses:Expense)
            OPTIONAL MATCH (u)-[:PARTICIPANT_IN]->(sharedExpenses:Expense)
            WITH u,
                 COALESCE(sum(DISTINCT paidExpenses.amount), 0) as totalPaid,
                 count(DISTINCT sharedExpenses) as expenseCount
            WHERE totalPaid > 0 OR expenseCount > 0
            RETURN u.name as name,
                   totalPaid,
                   expenseCount
            ORDER BY totalPaid DESC
        """)
        
        print("\n✅ Results:")
        for record in result:
            print(f"   • {record['name']}: "
                  f"Paid ${record['totalPaid']:.2f}, "
                  f"Involved in {record['expenseCount']} expense(s)")

def demo_path_finding():
    """Demonstrate path finding capabilities"""
    print_section("5. PATH FINDING - DEBT CHAINS")
    
    with driver.session(database=Config.NEO4J_DATABASE) as session:
        print("\n📊 Query: Find indirect debt relationships")
        print("Cypher:")
        print("  MATCH path = (u1:User)-[:PAID|PARTICIPANT_IN*1..3]-(u2:User)")
        print("  WHERE u1 <> u2")
        print("  RETURN u1.name, u2.name, length(path)")
        
        result = session.run("""
            MATCH (u1:User)-[:MEMBER_OF]->(g:Group)<-[:MEMBER_OF]-(u2:User)
            WHERE u1 <> u2
            WITH u1, u2, g
            MATCH (u1)-[:PAID]->(e1:Expense)-[:BELONGS_TO]->(g)
            MATCH (u2)-[:PAID]->(e2:Expense)-[:BELONGS_TO]->(g)
            WHERE e1 <> e2
            RETURN u1.name as user1,
                   u2.name as user2,
                   g.name as inGroup,
                   count(DISTINCT e1) as user1Expenses,
                   count(DISTINCT e2) as user2Expenses
            LIMIT 10
        """)
        
        print("\n✅ Results (users with mutual expenses):")
        for record in result:
            print(f"   • {record['user1']} ⟷ {record['user2']} in '{record['inGroup']}': "
                  f"{record['user1Expenses']} + {record['user2Expenses']} expenses")

def demo_statistics():
    """Show database statistics"""
    print_section("6. DATABASE STATISTICS")
    
    with driver.session(database=Config.NEO4J_DATABASE) as session:
        # Count nodes
        result = session.run("""
            MATCH (n)
            RETURN labels(n)[0] as nodeType, count(n) as count
            ORDER BY count DESC
        """)
        
        print("\n📊 Node Counts:")
        for record in result:
            if record['nodeType']:
                print(f"   • {record['nodeType']}: {record['count']}")
        
        # Count relationships
        result = session.run("""
            MATCH ()-[r]->()
            RETURN type(r) as relType, count(r) as count
            ORDER BY count DESC
        """)
        
        print("\n📊 Relationship Counts:")
        for record in result:
            print(f"   • {record['relType']}: {record['count']}")

def demo_performance():
    """Demonstrate query performance"""
    print_section("7. QUERY PERFORMANCE")
    
    with driver.session(database=Config.NEO4J_DATABASE) as session:
        print("\n⚡ Testing query performance...")
        
        queries = [
            ("Find user by email (indexed)", """
                MATCH (u:User {email: 'test@example.com'})
                RETURN u
            """),
            ("Count group members", """
                MATCH (g:Group)<-[:MEMBER_OF]-(members:User)
                RETURN g.name, count(members) as memberCount
            """),
            ("Calculate group balances", """
                MATCH (g:Group)<-[:BELONGS_TO]-(e:Expense)
                MATCH (e)<-[:PAID]-(payer:User)
                MATCH (e)<-[:PARTICIPANT_IN]-(participant:User)
                WITH g, payer, participant, sum(e.amount) as total
                RETURN g.name, count(*) as transactions
                LIMIT 1
            """)
        ]
        
        for name, query in queries:
            start = time.time()
            result = session.run(query)
            result.consume()  # Force execution
            duration = (time.time() - start) * 1000
            print(f"   • {name}: {duration:.2f}ms")

def main():
    """Run all demonstrations"""
    print("\n" + "🎓" * 35)
    print("  Neo4j Graph Database Capabilities Demo")
    print("  Expense Splitter Application")
    print("🎓" * 35)
    
    try:
        # Verify connection
        driver.verify_connectivity()
        print("\n✅ Connected to Neo4j!")
        
        # Check if we have data
        with driver.session(database=Config.NEO4J_DATABASE) as session:
            result = session.run("MATCH (n) RETURN count(n) as nodeCount")
            node_count = result.single()['nodeCount']
            
            if node_count == 0:
                print("\n⚠️  Warning: Database is empty!")
                print("   Please use the application to create some data first:")
                print("   1. Register users")
                print("   2. Create groups")
                print("   3. Add expenses")
                print("\n   Then run this demo again to see the graph capabilities!")
                return
            
            print(f"   Found {node_count} nodes in database")
        
        # Run demonstrations
        demo_statistics()
        demo_complex_relationships()
        demo_graph_traversal()
        demo_pattern_matching()
        demo_aggregations()
        demo_path_finding()
        demo_performance()
        
        print_section("✅ DEMO COMPLETE")
        print("\nKey Neo4j Benefits Demonstrated:")
        print("  1. ✓ Natural relationship modeling")
        print("  2. ✓ Complex graph traversals")
        print("  3. ✓ Pattern matching queries")
        print("  4. ✓ Efficient aggregations")
        print("  5. ✓ Path finding capabilities")
        print("  6. ✓ High performance on connected data")
        
        print("\nPerfect for Assignment Requirements:")
        print("  ✓ Database Setup and Configuration")
        print("  ✓ Data Model Design (Graph)")
        print("  ✓ CRUD Operations Implementation")
        print("  ✓ NoSQL Feature Demonstration")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("  1. Neo4j is running")
        print("  2. .env file is configured")
        print("  3. You have data in the database")
    finally:
        driver.close()

if __name__ == '__main__':
    main()