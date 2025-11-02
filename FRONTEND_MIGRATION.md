# Frontend Migration Guide

## Overview
This guide helps you connect your existing Next.js frontend to the Flask + Neo4j backend.

## Quick Start

### Option 1: Environment Variable (Recommended)

1. Create `.env.local` in your Next.js root:
```env
NEXT_PUBLIC_API_URL=http://localhost:5000/api
```

2. Update your API calls to use this variable:
```javascript
// Before
const res = await fetch('/api/expenses', { ... });

// After
const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/expenses`, { ... });
```

### Option 2: Next.js Rewrites (Alternative)

Add to `next.config.mjs`:
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:5000/api/:path*',
      },
    ];
  },
};

export default nextConfig;
```

This allows you to keep your existing `/api/*` calls without changes!

## Authentication Changes

### 1. Update NextAuth to Custom JWT

The Flask backend uses custom JWT tokens instead of NextAuth.

**Update your API calls to include the token:**

```javascript
// Store token after login
const handleLogin = async (email, password) => {
  const res = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  
  const data = await res.json();
  if (res.ok) {
    // Store token in localStorage or cookie
    localStorage.setItem('token', data.token);
    // Redirect to dashboard
  }
};

// Include token in subsequent requests
const createGroup = async (name) => {
  const token = localStorage.getItem('token');
  const res = await fetch(`${API_URL}/groups`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ name }),
  });
  return res.json();
};
```

### 2. Update Session Management

Replace `getServerSession` with custom session check:

```javascript
// Before (with NextAuth)
import { getServerSession } from "next-auth/next";
const session = await getServerSession(authOptions);

// After (with Flask JWT)
const getSession = async () => {
  const token = localStorage.getItem('token');
  if (!token) return null;
  
  const res = await fetch(`${API_URL}/auth/session`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  if (res.ok) {
    return await res.json();
  }
  return null;
};
```

### 3. Update AuthProvider

Create a new auth context:

```javascript
// components/AuthContext.jsx
'use client';
import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/session`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (res.ok) {
        const data = await res.json();
        setUser(data.user);
      } else {
        localStorage.removeItem('token');
      }
    } catch (error) {
      console.error('Auth check failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    
    if (res.ok) {
      const data = await res.json();
      localStorage.setItem('token', data.token);
      setUser(data.user);
      return { success: true };
    } else {
      const data = await res.json();
      return { success: false, error: data.error };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
```

## API Endpoint Mapping

### Authentication
```
POST /api/auth/[...nextauth] → POST /api/auth/login
POST /api/register           → POST /api/auth/register
```

### Groups
```
POST   /api/groups                    → POST   /api/groups
GET    /api/groups/[groupId]          → GET    /api/groups/<groupId>
DELETE /api/groups/[groupId]          → DELETE /api/groups/<groupId>
POST   /api/groups/[groupId]/members  → POST   /api/groups/<groupId>/members
```

### Expenses
```
POST /api/expenses → POST /api/expenses
```

### Settlements
```
POST /api/settlements → POST /api/settlements
```

## Response Format Changes

The Flask backend returns similar JSON structures, but with slight differences:

### Before (Prisma)
```json
{
  "id": "clx...",
  "name": "Group Name",
  "_count": { "members": 3 }
}
```

### After (Neo4j)
```json
{
  "id": "uuid...",
  "name": "Group Name",
  "_count": { "members": 3 }
}
```

**Note:** IDs are now UUIDs instead of CUID, but functionality remains the same.

## Testing Your Migration

1. **Start both servers:**
```bash
# Terminal 1 - Backend
cd backend
python app.py

# Terminal 2 - Frontend  
cd ..
npm run dev
```

2. **Test the flow:**
- Register a new user
- Login
- Create a group
- Add expenses
- Check balances

3. **Check browser console for any CORS or API errors**

## Common Issues

### CORS Errors
Make sure Flask CORS is configured for your frontend URL:
```python
# In backend/app.py
CORS(app, origins=["http://localhost:3000"])
```

### 401 Unauthorized
Check that:
- Token is being stored correctly
- Authorization header format is: `Bearer <token>`
- Token hasn't expired (24 hours by default)

### Network Errors
Verify:
- Flask server is running on port 5000
- No firewall blocking the connection
- API URL is correct in .env.local

## Need Help?

If you encounter issues:
1. Check the Flask server logs
2. Check browser console for errors
3. Use browser DevTools Network tab to inspect requests
4. Verify .env files are configured correctly