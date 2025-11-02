# Expense Splitter - Neo4j Backend

A Flask-based REST API backend using Neo4j graph database for the Expense Splitter application.

## 🎯 Project Overview

This project demonstrates the use of **Neo4j Graph Database** for managing complex relationships in an expense-splitting application. It showcases:

- **Graph Data Model**: Users, Groups, Expenses, and Settlements as nodes with meaningful relationships
- **Complex Queries**: Leveraging graph traversal for balance calculations and debt settlements
- **CRUD Operations**: Full Create, Read, Update, Delete functionality using Cypher queries
- **Relationship Benefits**: Efficient querying of interconnected data (who owes whom, group memberships, etc.)

## 📊 Graph Data Model

### Nodes
```
(:User {id, email, name, hashedPassword, createdAt})
(:Group {id, name, createdAt})
(:Expense {id, description, amount, createdAt})
(:Settlement {id, amount, paidAt})
```

### Relationships
```
(User)-[:MEMBER_OF]->(Group)
(User)-[:PAID]->(Expense)
(User)-[:PARTICIPANT_IN]->(Expense)
(Expense)-[:BELONGS_TO]->(Group)
(Settlement)-[:IN_GROUP]->(Group)
(Settlement)-[:FROM]->(User)
(Settlement)-[:TO]->(User)
```

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8+
- Neo4j Aura account (or local Neo4j instance)
- Node.js 16+ (for frontend)

### Step 1: Clone the Repository
```bash
git clone <your-repo-url>
cd project
```

### Step 2: Backend Setup

1. **Create virtual environment** (recommended)
```bash
cd backend
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your Neo4j credentials
nano .env  # or use your preferred editor
```

Add your Neo4j Aura credentials:
```env
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password_here
NEO4J_DATABASE=neo4j

SECRET_KEY=generate-a-random-secret-key-here
JWT_SECRET_KEY=generate-another-random-key-here
```

4. **Initialize the database**
```bash
python app.py
```

On first run, the application will automatically create:
- Uniqueness constraints for all node types
- Indexes for performance optimization

You should see output like:
```
✓ Created: (u:User)
✓ Created: (g:Group)
✓ Created: (e:Expense)
✓ Created: (s:Settlement)
✅ Database initialization complete!
```

5. **Run the Flask server**
```bash
python app.py
```

The API will be available at `http://localhost:5000`

### Step 3: Frontend Setup

1. **Navigate to frontend directory**
```bash
cd ../  # Go back to project root if in backend
# Your Next.js frontend should already be there
```

2. **Update API endpoints** (if needed)

The frontend needs to be configured to call the Flask backend instead of Next.js API routes. You have two options:

**Option A: Use a proxy (Recommended)**
Add to your `package.json`:
```json
{
  "proxy": "http://localhost:5000"
}
```

**Option B: Update API calls directly**
Change API calls from `/api/...` to `http://localhost:5000/api/...`

3. **Install dependencies** (if not already done)
```bash
npm install
```

4. **Run the development server**
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/session` - Get current session

### Groups
- `POST /api/groups` - Create new group
- `GET /api/groups/<id>` - Get group details
- `DELETE /api/groups/<id>` - Delete group
- `POST /api/groups/<id>/members` - Add member to group
- `GET /api/groups/user` - Get all user's groups

### Expenses
- `POST /api/expenses` - Create new expense
- `GET /api/expenses/<id>` - Get expense details
- `DELETE /api/expenses/<id>` - Delete expense
- `GET /api/expenses/group/<group_id>` - Get group expenses
- `GET /api/expenses/user` - Get user's expenses

### Settlements
- `POST /api/settlements` - Record a payment
- `GET /api/settlements/group/<group_id>` - Get group settlements
- `GET /api/settlements/balances/group/<group_id>` - Get balances and payment suggestions
- `GET /api/settlements/balances` - Get all balances across groups

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## 🧪 Testing the API

### Using curl

1. **Register a user**
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "password": "Password123"
  }'
```

2. **Login**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Password123"
  }'
```

Save the returned token for subsequent requests.

3. **Create a group**
```bash
curl -X POST http://localhost:5000/api/groups \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{
    "name": "Trip to Paris"
  }'
```

### Using Postman

Import the API endpoints and test them with the Postman collection (you can create one based on the endpoints above).

## 💡 Neo4j Benefits Demonstrated

### 1. **Relationship Queries**
Neo4j excels at querying relationships. Example: "Find all expenses where a user is involved":

```cypher
MATCH (u:User {id: $userId})
MATCH (e:Expense)
WHERE (u)-[:PAID]->(e) OR (u)-[:PARTICIPANT_IN]->(e)
RETURN e
```

### 2. **Graph Traversal**
Finding indirect relationships is natural:

```cypher
// Find all users in my groups
MATCH (me:User {id: $myId})-[:MEMBER_OF]->(g:Group)<-[:MEMBER_OF]-(others:User)
RETURN DISTINCT others
```

### 3. **Pattern Matching**
Complex patterns are easy to express:

```cypher
// Find expenses where I paid but others participated
MATCH (me:User {id: $myId})-[:PAID]->(e:Expense)<-[:PARTICIPANT_IN]-(others:User)
WHERE me <> others
RETURN e, others
```

### 4. **Aggregations**
Calculate balances efficiently:

```cypher
// Get total owed to a user
MATCH (u:User {id: $userId})-[:PAID]->(e:Expense)<-[:PARTICIPANT_IN]-(others:User)
WITH u, e, count(others) as numParticipants
RETURN sum(e.amount - (e.amount / numParticipants)) as totalOwed
```

## 📁 Project Structure

```
backend/
├── app.py                 # Flask application entry point
├── config.py              # Configuration management
├── database.py            # Neo4j connection and initialization
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
│
├── models/               # Data models (Neo4j operations)
│   ├── user.py
│   ├── group.py
│   ├── expense.py
│   └── settlement.py
│
├── routes/               # API route blueprints
│   ├── auth.py
│   ├── groups.py
│   ├── expenses.py
│   └── settlements.py
│
└── utils/                # Utility functions
    ├── auth.py           # JWT authentication
    └── calculations.py   # Balance calculations
```

## 🐛 Troubleshooting

### Connection Issues
- Verify your Neo4j Aura credentials in `.env`
- Check if your IP is whitelisted in Neo4j Aura
- Ensure the URI format is correct: `neo4j+s://...`

### Import Errors
- Make sure you're in the virtual environment
- Reinstall dependencies: `pip install -r requirements.txt`

### CORS Issues
- Verify the frontend URL in `app.py` CORS configuration
- Check browser console for specific CORS errors

## 📚 Assignment Documentation

### Database Setup and Configuration (5 marks)
- Neo4j Aura instance configured
- Constraints and indexes created automatically
- Connection pooling and session management

### Data Model Design (10 marks)
- Graph model with 4 node types and 7 relationship types
- Uniqueness constraints on IDs
- Indexes for performance optimization
- Clear separation of concerns in models

### CRUD Operations Implementation (10 marks)
- Complete CRUD for Users, Groups, Expenses, Settlements
- Graph-native queries using Cypher
- Proper error handling and validation
- RESTful API design

### NoSQL Feature Demonstration (5 marks)
- Complex relationship queries
- Graph traversal for balance calculations
- Pattern matching for debt simplification
- Efficient aggregations using graph structure

## 📝 License

This project is for educational purposes as part of the NoSQL Database course (BCSE406L).

## 👥 Author

Karthik Yadav - VIT University