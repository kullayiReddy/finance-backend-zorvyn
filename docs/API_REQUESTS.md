# API Requests & Examples

Complete guide with cURL examples for all endpoints.

## 🔐 Authentication Endpoints

### 1. Register New User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepass123",
    "full_name": "John Doe"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepass123"
  }'
```

**Response:** Same as register

### 3. Refresh Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

### 4. Get Current User Info

```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
{
  "id": 1,
  "email": "john@example.com",
  "full_name": "John Doe",
  "role": "viewer",
  "status": "active"
}
```

---

## 👥 User Management (Admin Only)

### 1. List All Users

```bash
curl -X GET "http://localhost:8000/api/v1/users/?skip=0&limit=10" \
  -H "Authorization: Bearer <ADMIN_TOKEN>"
```

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "email": "john@example.com",
      "full_name": "John Doe",
      "role": "viewer",
      "status": "active",
      "created_at": "2024-01-01T10:00:00",
      "updated_at": "2024-01-01T10:00:00"
    }
  ],
  "total": 50,
  "skip": 0,
  "limit": 10,
  "has_more": true
}
```

### 2. Get Specific User

```bash
curl -X GET http://localhost:8000/api/v1/users/1 \
  -H "Authorization: Bearer <ADMIN_TOKEN>"
```

### 3. Create User (Admin)

```bash
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "analyst@example.com",
    "password": "pass123",
    "full_name": "Jane Analyst",
    "role": "analyst"
  }'
```

### 4. Update User

```bash
curl -X PATCH http://localhost:8000/api/v1/users/1 \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Updated",
    "role": "analyst",
    "status": "inactive"
  }'
```

### 5. Delete User

```bash
curl -X DELETE http://localhost:8000/api/v1/users/1 \
  -H "Authorization: Bearer <ADMIN_TOKEN>"
```

**Response:** 204 No Content

### 6. Search User by Email

```bash
curl -X GET "http://localhost:8000/api/v1/users/search/email?email=john@example.com" \
  -H "Authorization: Bearer <ADMIN_TOKEN>"
```

---

## 💰 Financial Records

### 1. Create Record

```bash
curl -X POST http://localhost:8000/api/v1/records/ \
  -H "Authorization: Bearer <USER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 5000.00,
    "type": "income",
    "category": "Salary",
    "date": "2024-01-15T00:00:00",
    "notes": "Monthly salary"
  }'
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "amount": 5000.00,
  "type": "income",
  "category": "Salary",
  "date": "2024-01-15T00:00:00",
  "notes": "Monthly salary",
  "created_at": "2024-01-15T10:30:00"
}
```

### 2. List User's Records (with Pagination)

```bash
curl -X GET "http://localhost:8000/api/v1/records/?skip=0&limit=10" \
  -H "Authorization: Bearer <USER_TOKEN>"
```

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "user_id": 1,
      "amount": 5000.00,
      "type": "income",
      "category": "Salary",
      "date": "2024-01-15T00:00:00",
      "notes": "Monthly salary",
      "created_at": "2024-01-15T10:30:00"
    }
  ],
  "total": 50,
  "skip": 0,
  "limit": 10,
  "has_more": true
}
```

### 3. List Records with Filters

```bash
# Filter by category
curl -X GET "http://localhost:8000/api/v1/records/?category=Salary&limit=10" \
  -H "Authorization: Bearer <USER_TOKEN>"

# Filter by type
curl -X GET "http://localhost:8000/api/v1/records/?type=income&limit=10" \
  -H "Authorization: Bearer <USER_TOKEN>"

# Search in notes
curl -X GET "http://localhost:8000/api/v1/records/?search=monthly" \
  -H "Authorization: Bearer <USER_TOKEN>"

# Combined filters
curl -X GET "http://localhost:8000/api/v1/records/?category=Groceries&type=expense&limit=20" \
  -H "Authorization: Bearer <USER_TOKEN>"
```

### 4. Get Specific Record

```bash
curl -X GET http://localhost:8000/api/v1/records/1 \
  -H "Authorization: Bearer <USER_TOKEN>"
```

### 5. Update Record

```bash
curl -X PATCH http://localhost:8000/api/v1/records/1 \
  -H "Authorization: Bearer <USER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 5500.00,
    "notes": "Salary with bonus"
  }'
```

### 6. Delete Record

```bash
curl -X DELETE http://localhost:8000/api/v1/records/1 \
  -H "Authorization: Bearer <USER_TOKEN>"
```

### 7. Get Records by Date Range

```bash
curl -X GET "http://localhost:8000/api/v1/records/filter/by-date-range?start_date=2024-01-01&end_date=2024-01-31" \
  -H "Authorization: Bearer <USER_TOKEN>"
```

### 8. Get User's Categories

```bash
curl -X GET http://localhost:8000/api/v1/records/category/list \
  -H "Authorization: Bearer <USER_TOKEN>"
```

**Response:**
```json
["Salary", "Groceries", "Utilities", "Entertainment"]
```

---

## 📊 Dashboard & Analytics

### 1. Get Complete Dashboard Summary

```bash
curl -X GET http://localhost:8000/api/v1/dashboard/summary \
  -H "Authorization: Bearer <USER_TOKEN>"
```

**Response:**
```json
{
  "total_income": 15000.00,
  "total_expense": 5000.00,
  "net_balance": 10000.00,
  "category_wise": [
    {
      "category": "Salary",
      "income": 15000.00,
      "expense": 0.00,
      "net": 15000.00
    },
    {
      "category": "Groceries",
      "income": 0.00,
      "expense": 500.00,
      "net": -500.00
    }
  ],
  "monthly_trends": [
    {
      "month": "2024-01",
      "income": 5000.00,
      "expense": 2000.00,
      "net": 3000.00
    },
    {
      "month": "2024-02",
      "income": 5000.00,
      "expense": 1500.00,
      "net": 3500.00
    }
  ],
  "recent_records": [
    {
      "id": 1,
      "user_id": 1,
      "amount": 5000.00,
      "type": "income",
      "category": "Salary",
      "date": "2024-01-15T00:00:00",
      "notes": "Monthly salary",
      "created_at": "2024-01-15T10:30:00"
    }
  ]
}
```

### 2. Get Total Income

```bash
curl -X GET http://localhost:8000/api/v1/dashboard/total-income \
  -H "Authorization: Bearer <USER_TOKEN>"
```

**Response:**
```json
{
  "total_income": 15000.00,
  "currency": "USD"
}
```

### 3. Get Total Expense

```bash
curl -X GET http://localhost:8000/api/v1/dashboard/total-expense \
  -H "Authorization: Bearer <USER_TOKEN>"
```

**Response:**
```json
{
  "total_expense": 5000.00,
  "currency": "USD"
}
```

### 4. Get Net Balance

```bash
curl -X GET http://localhost:8000/api/v1/dashboard/net-balance \
  -H "Authorization: Bearer <USER_TOKEN>"
```

**Response:**
```json
{
  "net_balance": 10000.00,
  "currency": "USD"
}
```

### 5. Get Monthly Summary

```bash
curl -X GET "http://localhost:8000/api/v1/dashboard/monthly/2024/01" \
  -H "Authorization: Bearer <USER_TOKEN>"
```

**Response:**
```json
{
  "month": "2024-01",
  "income": 5000.00,
  "expense": 2000.00,
  "net": 3000.00
}
```

### 6. Get Quick Stats

```bash
curl -X GET http://localhost:8000/api/v1/dashboard/quick-stats \
  -H "Authorization: Bearer <USER_TOKEN>"
```

**Response:**
```json
{
  "total_income": 15000.00,
  "total_expense": 5000.00,
  "net_balance": 10000.00,
  "user_role": "viewer",
  "currency": "USD"
}
```

### 7. Get Admin Statistics (Analyst+ only)

```bash
curl -X GET http://localhost:8000/api/v1/dashboard/admin/stats \
  -H "Authorization: Bearer <ANALYST_TOKEN>"
```

**Response:**
```json
{
  "total_records": 1250,
  "total_users_with_records": 85,
  "system_income": 500000.00,
  "system_expense": 250000.00,
  "net_flow": 250000.00,
  "accessed_by": "analyst@example.com"
}
```

---

## ⚠️ Error Responses

### 401 Unauthorized (Invalid Token)

```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden (Insufficient Permissions)

```json
{
  "detail": "Admin access required"
}
```

### 404 Not Found

```json
{
  "detail": "User not found"
}
```

### 400 Bad Request (Validation Error)

```json
{
  "detail": [
    {
      "loc": ["body", "amount"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

---

## 🧪 Testing Workflow

### Step 1: Register User

```bash
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123",
    "full_name": "Test User"
  }')

TOKEN=$(echo $RESPONSE | jq -r '.access_token')
echo "Token: $TOKEN"
```

### Step 2: Create Records

```bash
# Income record
curl -X POST http://localhost:8000/api/v1/records/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 3000,
    "type": "income",
    "category": "Salary",
    "notes": "Monthly salary"
  }'

# Expense record
curl -X POST http://localhost:8000/api/v1/records/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 500,
    "type": "expense",
    "category": "Groceries",
    "notes": "Weekly groceries"
  }'
```

### Step 3: View Dashboard

```bash
curl -X GET http://localhost:8000/api/v1/dashboard/summary \
  -H "Authorization: Bearer $TOKEN" | jq
```

---

## 📝 Notes

- Replace `<USER_TOKEN>`, `<ADMIN_TOKEN>`, `<ANALYST_TOKEN>` with actual tokens
- All timestamps are in ISO 8601 format
- All amounts are in floating point (USD)
- `limit` parameter max is 100
- Pagination uses `skip` and `limit` (not page-based)
- Empty lists return `has_more: false`

---

## 🔗 Quick Links

- **API Documentation**: http://localhost:8000/docs
- **Alternative Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
