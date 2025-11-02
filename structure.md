backend/
├── app.py                    # Flask application entry point
├── config.py                 # Configuration management
├── database.py               # Neo4j connection & init
├── requirements.txt          # Python dependencies
├── .env.example             # Environment template
│
├── models/                   # Data models
│   ├── user.py              # User operations
│   ├── group.py             # Group operations
│   ├── expense.py           # Expense operations
│   └── settlement.py        # Settlement operations
│
├── routes/                   # API routes
│   ├── auth.py              # Authentication endpoints
│   ├── groups.py            # Group endpoints
│   ├── expenses.py          # Expense endpoints
│   └── settlements.py       # Settlement endpoints
│
├── utils/                    # Utilities
│   ├── auth.py              # JWT authentication
│   └── calculations.py      # Balance calculations
│
├── Documentation/
│   ├── README.md
│   ├── ASSIGNMENT_DOCUMENTATION.md
│   ├── FRONTEND_MIGRATION.md
│   ├── QUICK_START_GUIDE.md
│   └── ASSIGNMENT_CHECKLIST.md
│
└── Tools/
    ├── test_connection.py        # Connection test
    ├── demo_graph_capabilities.py # Feature demo
    └── setup.sh                   # Setup script