# Architecture & Design Decisions

## 🏗️ Overall Architecture Pattern

This project uses **Layered Architecture** (also known as N-Tier Architecture), which separates concerns into distinct layers:

```
┌─────────────────────────────────────────┐
│        API Layer (Routes)               │
│  - Request routing                      │
│  - Request/response validation          │
│  - RBAC enforcement                     │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│      Business Logic Layer (Services)    │
│  - Core business rules                  │
│  - Data processing                      │
│  - Authentication logic                 │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│      Data Access Layer (ORM Models)     │
│  - Database queries                     │
│  - Data persistence                     │
│  - Relationships                        │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│        Database (SQLite)                │
└─────────────────────────────────────────┘
```

## 📁 Directory Organization

### By Responsibility

```
Finance/
├── main.py                      # FastAPI app + route registration
├── config.py                    # Configuration management
├── database.py                  # Database connection & setup
│
├── Models Layer:
│   └── models.py                # SQLAlchemy ORM models
│
├── Schema Layer (DTOs):
│   └── schemas.py               # Pydantic validation schemas
│
├── Services Layer:
│   ├── token_service.py         # JWT token operations
│   ├── user_service.py          # User CRUD & authentication
│   ├── record_service.py        # Financial record operations
│   └── dashboard_service.py     # Analytics & aggregations
│
├── Routes Layer:
│   ├── auth_routes.py           # Authentication endpoints
│   ├── user_routes.py           # User management endpoints
│   ├── record_routes.py         # Record management endpoints
│   └── dashboard_routes.py      # Analytics endpoints
│
└── Middleware:
    └── auth_middleware.py       # Authentication & RBAC
```

## 🔄 Data Flow Explanation

### Example: Creating a Financial Record

```
1. CLIENT REQUEST
   POST /api/v1/records/
   Body: { amount: 100, type: "income", ... }
   Header: Authorization: Bearer <TOKEN>

2. AUTH MIDDLEWARE (auth_middleware.py)
   ├─ Extract token from header
   ├─ Verify JWT signature
   ├─ Extract user_id from token
   └─ Load User object from database
       └─ Return CurrentUser dependency

3. ROUTE HANDLER (record_routes.py)
   ├─ Receive CurrentUser & RecordCreate schema
   ├─ Validate RecordCreate using Pydantic (automatic)
   ├─ Call RecordService.create_record()
   └─ Return RecordResponse

4. SERVICE LAYER (record_service.py)
   ├─ Validate business rules
   ├─ Create FinancialRecord ORM object
   ├─ Add to database session
   ├─ Commit transaction
   └─ Return FinancialRecord object

5. ORM LAYER (models.py)
   ├─ SQLAlchemy converts Python object
   ├─ Generates INSERT SQL
   ├─ Executes SQL against SQLite
   └─ Auto-generates timestamps & ID

6. DATABASE (finance.db)
   ├─ Inserts row into financial_records table
   └─ Returns inserted row with ID

7. RESPONSE TRANSFORMATION
   ├─ RecordResponse validates ORM object
   ├─ Converts to JSON
   └─ Returns to client

8. CLIENT RESPONSE
   200 OK
   {
     "id": 1,
     "user_id": 1,
     "amount": 100,
     "type": "income",
     ...
   }
```

## 🔐 Role-Based Access Control (RBAC) Implementation

### Architecture

```
Request
   │
   ▼
Auth Middleware (Verify JWT)
   │
   ├─ Extract token
   ├─ Verify signature
   └─ Load User from DB
   │
   ▼
RBAC Dependency
   │
   ├─ require_admin()
   ├─ require_analyst_or_admin()
   ├─ require_role(*roles)
   └─ CurrentUser (any authenticated user)
   │
   ▼
Route Handler Execution
   │
   ▼
Response
```

### Code Example

**Step 1: Define Protected Route**
```python
@router.get("/admin-only")
def admin_endpoint(
    current_user: CurrentUser = Depends(require_admin)
):
    # current_user.user has been verified as Admin
    return {"message": "Admin access"}
```

**Step 2: How It Works**
1. Request comes in with Bearer token
2. `require_admin` dependency is invoked
3. `require_admin` depends on `CurrentUser`
4. `CurrentUser.__init__` extracts and verifies JWT
5. JWT payload has user_id and role
6. User loaded from database
7. Role is checked: `if user.role != UserRole.ADMIN: raise 403`
8. If passed, route handler executes

**Step 3: Permission Matrix**

| Endpoint | Method | Admin | Analyst | Viewer | Notes |
|----------|--------|:-----:|:-------:|:------:|-------|
| `/users/` | GET | ✅ | ❌ | ❌ | Only admins list users |
| `/users/{id}` | GET | ✅ | ❌ | ✅* | Can view own profile |
| `/users/{id}` | PATCH | ✅ | ❌ | ✅* | Can update own name only |
| `/records/` | POST | ✅ | ✅ | ❌ | Analyst can create |
| `/records/` | GET | ✅ | ✅ | ✅ | Everyone can view own |
| `/dashboard/summary` | GET | ✅ | ✅ | ✅ | Own dashboard only |
| `/dashboard/admin/stats` | GET | ✅ | ✅ | ❌ | System-wide stats |

## 🔑 Authentication & Token Flow

### JWT Token Structure

```python
# Token Payload
{
    "sub": "user@example.com",      # Subject (email)
    "user_id": 1,                   # User ID
    "role": "admin",                # User role
    "type": "access",               # Token type
    "exp": 1234567890,              # Expiration timestamp
    "iat": 1234567800               # Issued at timestamp
}

# Access Token Expiry: 30 minutes
# Refresh Token Expiry: 7 days
```

### Token Generation Flow

```python
# User logs in
1. POST /auth/login
   ├─ Authenticate(email, password)
   ├─ Verify password hash
   ├─ Load user from DB
   └─ If valid: create tokens

2. TokenService.create_tokens()
   ├─ Create token_data dict
   ├─ Call create_access_token()
   │  ├─ Add exp = now + 30 min
   │  ├─ Add type = "access"
   │  └─ Encode with SECRET_KEY + HS256
   ├─ Call create_refresh_token()
   │  ├─ Add exp = now + 7 days
   │  ├─ Add type = "refresh"
   │  └─ Encode with SECRET_KEY + HS256
   └─ Return {access_token, refresh_token}

3. Return to client:
   {
     "access_token": "eyJh...",
     "refresh_token": "eyJh...",
     "expires_in": 1800
   }

4. Client stores tokens and uses:
   - access_token: For all API requests
   - refresh_token: When access_token expires
```

### Token Refresh Flow

```
Access Token Expired
   │
   ▼
POST /auth/refresh
├─ Send refresh_token
│
▼
TokenService.verify_token(refresh_token)
├─ Verify JWT signature
├─ Check expiration
├─ Verify type == "refresh"
└─ Extract user_id
│
▼
Load User from DB
├─ Verify user still exists
├─ Verify user is active
│
▼
Create new access_token
├─ New exp = now + 30 min
└─ Encode with same user_id
│
▼
Return new access_token
│
▼
Client uses new access_token
```

## 🏢 Service Layer Design

### Separation of Concerns

**Why Services Exist:**
- Isolate business logic from HTTP concerns
- Enable unit testing without mocking FastAPI
- Reusable logic across multiple endpoints
- Clear responsibilities

### Service Organization

```python
# Example: UserService

class UserService:
    @staticmethod
    def create_user(db, user_data):
        # Business logic for user creation
        # - Validation
        # - Email uniqueness check
        # - Password hashing
        # - Database insert
        
    @staticmethod
    def authenticate_user(db, email, password):
        # Business logic for authentication
        # - Find user by email
        # - Compare password hash
        # - Check if user is active
        # - Return authenticated user
```

### Why Not Put Logic in Routes?

**❌ Bad (Mixed concerns):**
```python
@router.post("/records/")
def create_record(record_data, current_user, db):
    # SQL query
    query = db.query(User).filter(User.id == current_user.id)
    # Business logic
    if query.first().role != "analyst":
        raise HTTPException(...)
    # More business logic
    record = FinancialRecord(...)
    db.add(record)
    db.commit()
    # Return response
    return RecordResponse(record)
```

**✅ Good (Separated concerns):**
```python
@router.post("/records/")
def create_record(
    record_data: RecordCreate,
    current_user: CurrentUser = Depends(require_analyst_or_admin),
    db: Session = Depends(get_db)
):
    record = RecordService.create_record(db, current_user.user.id, record_data)
    return RecordResponse.model_validate(record)
```

Benefits:
- Route is 3 lines instead of 15
- RecordService is testable independently
- Logic is reusable
- Clear intent

## 🗄️ Database Design

### Schema Design Principles

```python
# 1. NORMALIZATION
# ✅ Good: Separate users and records
class User(Base):
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)

class FinancialRecord(Base):
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)

# ❌ Bad: Duplicate user data in each record
class FinancialRecord(Base):
    user_email = Column(String)  # Redundant!
    user_name = Column(String)   # Redundant!
```

### Relationships

```python
# One-to-Many Relationship
class User(Base):
    records = relationship(
        "FinancialRecord",
        back_populates="user",
        cascade="all, delete-orphan"
    )

class FinancialRecord(Base):
    user = relationship("User", back_populates="records")

# Usage:
user = db.query(User).first()
user.records  # All financial records for this user
```

### Indexes for Performance

```python
# Fast lookups
user_id = Column(Integer, ForeignKey("users.id"), index=True)
email = Column(String, unique=True, index=True)  # Unique implies index
type = Column(Enum(RecordType), index=True)      # Filter by type
category = Column(String, index=True)             # Filter by category
date = Column(DateTime, index=True)               # Filter by date
```

## ✅ Validation Strategy

### Three Levels of Validation

```
Level 1: Pydantic Schema Validation
   ├─ Type checking (string, int, float)
   ├─ Range validation (gt=0, le=100)
   ├─ Format validation (email, url)
   ├─ Custom validators
   └─ Automatic error messages

Level 2: Business Logic Validation
   ├─ Email uniqueness
   ├─ Password strength
   ├─ User exists
   └─ Custom rules

Level 3: Database Constraints
   ├─ Unique constraints
   ├─ Foreign key constraints
   ├─ Check constraints
   └─ NOT NULL constraints
```

### Example: Creating a Record

```python
# Level 1: Pydantic validates schema
@router.post("/records/")
def create_record(
    record_data: RecordCreate  # ← Pydantic validates here
    # - amount: float (must be positive)
    # - type: RecordType (must be 'income' or 'expense')
    # - category: str (min_length=1)
):
    # Level 2: Business logic validation
    if record_data.amount <= 0:
        raise ValueError("Amount must be positive")
    
    # Level 3: Database will enforce
    record = FinancialRecord(...)
    db.add(record)
    db.commit()  # DB checks constraints
```

## 🧪 Testability

### Why This Architecture is Testable

**Service Testing (No DB needed):**
```python
def test_password_hashing():
    hashed = TokenService.hash_password("password123")
    assert TokenService.verify_password("password123", hashed)
    assert not TokenService.verify_password("wrong", hashed)
```

**Service Testing (With Mock DB):**
```python
def test_create_user():
    mock_db = MagicMock()
    user_data = UserCreate(...)
    
    UserService.create_user(mock_db, user_data)
    
    assert mock_db.add.called
    assert mock_db.commit.called
```

**Route Testing (With TestClient):**
```python
def test_login():
    response = client.post(
        "/auth/login",
        json={"email": "admin@example.com", "password": "admin123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
```

## 🎯 Key Design Decisions Explained

### 1. Why Stateless JWT Instead of Session Cookies?

**JWT Advantages:**
- ✅ Horizontal scaling (no server state)
- ✅ Works across multiple servers
- ✅ Mobile-friendly
- ✅ CORS-friendly
- ✅ Microservices-ready

**Disadvantages:**
- Token size (larger than session ID)
- No built-in logout (requires blacklist)
- Token can't be revoked immediately

**Our approach:** Stateless for scalability, client-side logout

### 2. Why Decorator-Based RBAC?

**Alternatives:**
- ❌ Manual checks in routes (repetitive)
- ❌ Route groups (inflexible)
- ✅ Decorators (clean, reusable)

**Our approach:**
```python
@require_admin  # Clear, concise, reusable
def admin_route(current_user):
    pass
```

### 3. Why Services Between Routes and Models?

**Direct Route to Model (❌ Bad):**
```python
@app.post("/")
def endpoint(db):
    record = db.query(Record).filter(...).first()
    # Business logic mixed with database code
```

**With Services (✅ Good):**
```python
@app.post("/")
def endpoint():
    record = RecordService.get_record()
    # Clean separation
```

### 4. Why Pydantic Schemas?

**Benefits:**
- ✅ Automatic validation
- ✅ Type hints for IDE
- ✅ Auto-generated OpenAPI docs
- ✅ JSON serialization
- ✅ Backwards compatibility

### 5. Why SQLAlchemy ORM?

**Advantages:**
- ✅ SQL injection prevention
- ✅ Database agnostic (easy to migrate to PostgreSQL)
- ✅ Relationships simplified
- ✅ Query builder

## 📊 Performance Considerations

### Current Optimizations

1. **Indexing:** Frequently filtered columns indexed
2. **Pagination:** Prevent loading huge datasets
3. **Lazy Loading:** Relationships load on demand
4. **Connection Pooling:** (SQLAlchemy default)

### Future Improvements

```python
# 1. Add Redis caching
cache.get("user:1:dashboard")

# 2. Add query optimization
db.query(Record).options(joinedload(Record.user))

# 3. Add batch operations
db.query(Record).filter(...).update({...})

# 4. Add database connection pooling
engine = create_engine(..., pool_size=10)
```

---

This architecture is designed to be:
- ✅ **Clean** - Easy to understand and modify
- ✅ **Testable** - Each layer can be tested independently
- ✅ **Scalable** - Stateless, ready for horizontal scaling
- ✅ **Maintainable** - Clear responsibilities
- ✅ **Production-ready** - Industry-standard patterns
