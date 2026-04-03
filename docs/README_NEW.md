# Finance Dashboard Backend - README

## 📊 Project Overview

A **production-quality backend system** for a Finance Data Processing and Access Control Dashboard. This project demonstrates:

- ✅ Clean Architecture (Layered Architecture)
- ✅ Role-Based Access Control (RBAC)
- ✅ JWT Authentication with Refresh Tokens
- ✅ RESTful API with FastAPI
- ✅ SQLAlchemy ORM with SQLite
- ✅ Comprehensive Input Validation
- ✅ Pagination & Search
- ✅ Dashboard Analytics
- ✅ Proper Error Handling
- ✅ API Documentation (Swagger UI & ReDoc)

## 🎯 Key Features

### 1. **User Management with Roles**
- **3 User Roles**:
  - **Admin**: Full access (CRUD users, records, system admin functions)
  - **Analyst**: Read records & analytics, system-wide statistics
  - **Viewer**: Read-only access to own dashboard
- User status: Active/Inactive
- User authentication with email & password

### 2. **Financial Records Management**
Each record contains:
- Amount (positive numeric)
- Type: Income or Expense
- Category (e.g., Salary, Groceries, Utilities)
- Date
- Notes (optional)

**APIs**:
- Create, Read, Update, Delete records
- Filter by date range, category, type
- Search in notes
- Pagination support

### 3. **Dashboard Analytics**
Get insights with endpoints for:
- Total income
- Total expenses
- Net balance (income - expenses)
- Category-wise breakdown
- Monthly trends
- Recent activity (last 10 records)
- System-wide statistics (Analyst+)

### 4. **Authentication & Authorization**
- JWT tokens (Access & Refresh)
- Stateless authentication
- Decorator-based RBAC enforcement
- Token refresh mechanism
- Automatic token expiration

### 5. **API Documentation**
- Interactive Swagger UI at `/docs`
- ReDoc at `/redoc`
- Request/response examples
- Error descriptions

## 🏗️ Architecture

### Layered Architecture

```
FastAPI App (Routes)
        ↓
    Services (Business Logic)
        ↓
    ORM Models (Database Layer)
        ↓
    SQLite Database
```

### Project Structure

```
Finance/
├── main.py                  # FastAPI app initialization & routes inclusion
├── config.py               # Configuration & environment settings
├── database.py             # Database setup & session management
├── models.py               # SQLAlchemy ORM models
├── schemas.py              # Pydantic request/response validation
│
├── Services (Business Logic):
│   ├── token_service.py    # JWT token generation & verification
│   ├── user_service.py     # User CRUD & authentication
│   ├── record_service.py   # Financial record operations
│   └── dashboard_service.py# Analytics & aggregations
│
├── Routes (API Endpoints):
│   ├── auth_routes.py      # Login, Register, Token Refresh
│   ├── user_routes.py      # User management (Admin only)
│   ├── record_routes.py    # Record CRUD & filtering
│   └── dashboard_routes.py # Analytics endpoints
│
├── Middleware:
│   └── auth_middleware.py  # JWT verification & RBAC checks
│
├── docs/
│   ├── API_REQUESTS.md     # Sample cURL requests
│   └── ARCHITECTURE.md     # Detailed architecture
│
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── finance.db             # SQLite database (auto-created)
```

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- pip

### 2. Install Dependencies

```bash
pip install -r requirements_new.txt
```

### 3. Setup Environment

Create `.env` file (optional - defaults are provided):

```env
DEBUG=True
SECRET_KEY=your-super-secret-key-change-in-production
DATABASE_URL=sqlite:///./finance.db
```

### 4. Initialize Database

```bash
python -c "from database import init_db; init_db(); print('Database initialized!')"
```

### 5. Create Admin User

```bash
python setup_admin.py
```

### 6. Run the Server

```bash
python main.py
```

Server starts at: `http://localhost:8000`

### 7. Access Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔐 Role-Based Access Control (RBAC)

### Permission Matrix

| Operation | Admin | Analyst | Viewer |
|-----------|:-----:|:-------:|:------:|
| **User Management** | | | |
| Create User | ✅ | ❌ | ❌ |
| List Users | ✅ | ❌ | ❌ |
| Update User | ✅ | ❌ | ❌ |
| Delete User | ✅ | ❌ | ❌ |
| **Financial Records** | | | |
| Create Record | ✅ | ✅ | ❌ |
| View Own Records | ✅ | ✅ | ✅ |
| Edit Own Record | ✅ | ✅ | ❌ |
| Delete Own Record | ✅ | ✅ | ❌ |
| **Dashboard** | | | |
| View Own Dashboard | ✅ | ✅ | ✅ |
| System Statistics | ✅ | ✅ | ❌ |
| User Statistics | ✅ | ❌ | ❌ |

### RBAC Implementation

**Location**: `auth_middleware.py`

**Key Components**:
1. **`CurrentUser`**: Dependency that verifies JWT and extracts user
2. **`require_admin()`**: Checks if user is Admin
3. **`require_analyst_or_admin()`**: Checks if user is Analyst or Admin
4. **`require_role(*roles)`**: Generic role checker

**Usage in Routes**:

```python
# Admin only
def admin_endpoint(current_user: CurrentUser = Depends(require_admin)):
    pass

# Analyst or Admin
def stats_endpoint(current_user: CurrentUser = Depends(require_analyst_or_admin)):
    pass

# Any authenticated user
def user_dashboard(current_user: CurrentUser = Depends()):
    pass
```

## 🔑 Authentication Flow

### Registration & Login

```
1. POST /api/v1/auth/register
   └─→ Create user, return JWT tokens

2. POST /api/v1/auth/login
   └─→ Authenticate user, return JWT tokens

3. POST /api/v1/auth/refresh
   └─→ Use refresh token to get new access token
```

### Token Structure

```json
// Access Token (30 minutes)
{
  "sub": "user@example.com",
  "user_id": 1,
  "role": "admin",
  "type": "access",
  "exp": 1234567890
}

// Refresh Token (7 days)
{
  "sub": "user@example.com",
  "user_id": 1,
  "role": "admin",
  "type": "refresh",
  "exp": 1234567890
}
```

## 📚 API Endpoints

### Authentication

```
POST   /api/v1/auth/register        Register new user
POST   /api/v1/auth/login           Login with email & password
POST   /api/v1/auth/refresh         Refresh access token
POST   /api/v1/auth/logout          Logout (client-side)
GET    /api/v1/auth/me              Get current user info
```

### User Management (Admin only)

```
GET    /api/v1/users/               List all users (paginated)
GET    /api/v1/users/{id}           Get user by ID
POST   /api/v1/users/               Create new user
PATCH  /api/v1/users/{id}           Update user
DELETE /api/v1/users/{id}           Delete user
GET    /api/v1/users/search/email   Search user by email
```

### Financial Records

```
POST   /api/v1/records/             Create record
GET    /api/v1/records/             List records (with filters)
GET    /api/v1/records/{id}         Get record by ID
PATCH  /api/v1/records/{id}         Update record
DELETE /api/v1/records/{id}         Delete record
GET    /api/v1/records/filter/by-date-range    Date range filter
GET    /api/v1/records/category/list             Get categories
```

### Dashboard & Analytics

```
GET    /api/v1/dashboard/summary       Complete dashboard summary
GET    /api/v1/dashboard/total-income  Total income
GET    /api/v1/dashboard/total-expense Total expense
GET    /api/v1/dashboard/net-balance   Net balance
GET    /api/v1/dashboard/monthly/{year}/{month}  Monthly summary
GET    /api/v1/dashboard/quick-stats   Quick statistics
GET    /api/v1/dashboard/admin/stats   System statistics (Analyst+)
```

## 📊 Database Schema

### Users Table

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    full_name VARCHAR NOT NULL,
    role ENUM('admin', 'analyst', 'viewer') DEFAULT 'viewer',
    status ENUM('active', 'inactive') DEFAULT 'active',
    created_at DATETIME DEFAULT NOW,
    updated_at DATETIME DEFAULT NOW
);
```

### Financial Records Table

```sql
CREATE TABLE financial_records (
    id INTEGER PRIMARY KEY,
    user_id INTEGER FOREIGN KEY,
    amount FLOAT NOT NULL,
    type ENUM('income', 'expense') NOT NULL,
    category VARCHAR NOT NULL,
    date DATETIME NOT NULL,
    notes VARCHAR,
    created_at DATETIME DEFAULT NOW
);
```

## 🧪 Testing

### Run Tests

```bash
pytest tests/ -v
```

### Sample Test

```python
def test_login(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "admin123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
```

## 🔍 Sample API Requests

See `API_REQUESTS.md` for detailed examples with:
- cURL commands
- Response examples
- Error cases
- Different user roles

### Quick Example

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass123","full_name":"John Doe"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass123"}'

# Create record (with token)
curl -X POST http://localhost:8000/api/v1/records/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"amount":100,"type":"income","category":"Salary"}'
```

## 💡 Key Design Decisions

### 1. **Clean Architecture**
- **Why**: Separation of concerns, testability, maintainability
- **How**: Routes → Services → Models
- **Benefit**: Easy to unit test services independently

### 2. **Stateless JWT Authentication**
- **Why**: Scalable, no session storage needed
- **How**: Tokens contain all necessary info
- **Benefit**: Horizontal scaling without shared state

### 3. **Middleware-Based RBAC**
- **Why**: Declarative, reusable, centralized
- **How**: Decorators on endpoints
- **Benefit**: Clear permissions, easy to audit

### 4. **SQLite for Simplicity**
- **Why**: Single file, no setup, portable
- **How**: Works with SQLAlchemy ORM
- **Benefit**: Easy for interviews, upgradable to PostgreSQL

### 5. **Pydantic for Validation**
- **Why**: Automatic validation, documentation
- **How**: Schema-driven design
- **Benefit**: Type safety, auto-generated OpenAPI docs

## 🛡️ Security Features

- ✅ Password hashing with bcrypt
- ✅ JWT tokens with expiration
- ✅ RBAC enforcement
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ CORS configuration
- ✅ Email validation
- ✅ Input validation (Pydantic)
- ✅ HTTP-only recommended (configure on frontend)

## 📈 Bonus Features Implemented

1. ✅ **JWT Authentication** - Full token-based auth
2. ✅ **Pagination** - Limit-offset pagination on all list endpoints
3. ✅ **Search Functionality** - Search in notes, filter by category/type/date
4. ✅ **API Documentation** - Swagger UI & ReDoc
5. ✅ **Unit Tests** - Comprehensive test suite

## 🔧 Production Considerations

### Deployment Checklist

- [ ] Update `SECRET_KEY` in `.env` (use secure random string)
- [ ] Set `DEBUG=False`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Configure environment variables properly
- [ ] Set up HTTPS/SSL
- [ ] Configure CORS for frontend domain
- [ ] Set up proper logging
- [ ] Implement rate limiting
- [ ] Add database backups
- [ ] Monitor API performance

### Scaling Improvements

```python
# Current: SQLite
# Production: PostgreSQL

# Current: Single instance
# Production: Multiple instances with load balancer

# Current: No caching
# Production: Redis for token blacklist, query caching

# Current: No rate limiting
# Production: Use slowapi or similar
```

## ❓ FAQ

**Q: How do I create an admin user?**
A: Run `python setup_admin.py` or use the registration endpoint with role set to admin.

**Q: How do I add more categories?**
A: Categories are dynamic - any string is accepted. Users can create their own.

**Q: Can users see other users' records?**
A: No, users can only access their own records. Admins can view any user's records.

**Q: How do I change user role?**
A: Admin can update users: `PATCH /api/v1/users/{id}` with `{"role": "analyst"}`

**Q: What happens when a token expires?**
A: Use refresh token to get new access token via `POST /api/v1/auth/refresh`

## 📞 Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review `API_REQUESTS.md` for examples
3. Check database schema in `models.py`
4. Review RBAC implementation in `auth_middleware.py`

## 📄 License

This is a demonstration project for interview purposes.

---

**Built with ❤️ using FastAPI, SQLAlchemy, and Clean Architecture**
