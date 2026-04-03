# Setup & Installation Guide

## ✅ Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git (optional, for version control)

## 📦 Installation Steps

### Step 1: Prepare Environment

```bash
# Navigate to project directory
cd C:\Users\saida\Finance

# (Optional) Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements_new.txt
```

**What gets installed:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `sqlalchemy` - ORM
- `pydantic` - Data validation
- `python-jose` - JWT tokens
- `passlib` - Password hashing
- `pytest` - Testing framework

### Step 3: Configure Environment (Optional)

Create `.env` file:

```bash
# Copy example
copy .env.example .env

# Edit if needed (or use defaults)
```

**Key settings in `.env`:**
- `DEBUG=True` (for development)
- `SECRET_KEY` (change in production)
- `DATABASE_URL=sqlite:///./finance.db`

### Step 4: Initialize Database

```bash
# Option 1: Automatic (when app starts)
# Database creates automatically on first run

# Option 2: Manual
python setup_admin_new.py
```

### Step 5: Create Admin User

```bash
python setup_admin_new.py
```

**Creates three test users:**
- Admin: `admin@example.com` / `admin123`
- Analyst: `analyst@example.com` / `analyst123`
- Viewer: `viewer@example.com` / `viewer123`

### Step 6: Start the Server

```bash
python main.py
```

**Expected output:**
```
╔════════════════════════════════════════════════════════╗
║       Finance Dashboard Backend Server Starting       ║
╠════════════════════════════════════════════════════════╣
║ App: Finance Dashboard Backend                        ║
║ Version: 1.0.0                                         ║
║ Debug: True                                            ║
║ Database: sqlite:///./finance.db                       ║
╠════════════════════════════════════════════════════════╣
║ Swagger UI: http://localhost:8000/docs                ║
║ ReDoc: http://localhost:8000/redoc                    ║
╚════════════════════════════════════════════════════════╝

INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Step 7: Verify Installation

Open browser and visit:
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🚀 Running the Server

### Development Mode (with hot reload)

```bash
python main.py
# Or with uvicorn directly:
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🧪 Testing the API

### Test 1: Health Check

```bash
curl http://localhost:8000/health
```

### Test 2: Register User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123",
    "full_name": "Test User"
  }'
```

### Test 3: Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123"
  }'
```

Keep the `access_token` from response for next tests.

### Test 4: Create Financial Record

```bash
# Set token variable
$TOKEN = "your_access_token_here"

curl -X POST http://localhost:8000/api/v1/records/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 5000,
    "type": "income",
    "category": "Salary",
    "notes": "Monthly salary"
  }'
```

### Test 5: Get Dashboard

```bash
curl -X GET http://localhost:8000/api/v1/dashboard/summary \
  -H "Authorization: Bearer $TOKEN"
```

## 📁 Project Files

### Core Files

| File | Purpose |
|------|---------|
| `main.py` | FastAPI app initialization |
| `config.py` | Configuration & settings |
| `database.py` | Database connection |
| `models.py` | SQLAlchemy ORM models |
| `schemas.py` | Pydantic validation schemas |

### Service Layer

| File | Purpose |
|------|---------|
| `token_service.py` | JWT & password operations |
| `user_service.py` | User management |
| `record_service.py` | Financial records |
| `dashboard_service.py` | Analytics & reports |

### Routes Layer

| File | Purpose |
|------|---------|
| `auth_routes.py` | Authentication endpoints |
| `user_routes.py` | User management endpoints |
| `record_routes.py` | Record CRUD endpoints |
| `dashboard_routes.py` | Analytics endpoints |

### Middleware

| File | Purpose |
|------|---------|
| `auth_middleware.py` | JWT verification & RBAC |

### Documentation

| File | Purpose |
|------|---------|
| `README_NEW.md` | Project overview |
| `ARCHITECTURE.md` | Architecture details |
| `API_REQUESTS.md` | Sample API requests |
| `SETUP_GUIDE.md` | This file |
| `.env.example` | Environment template |

### Utilities

| File | Purpose |
|------|---------|
| `requirements_new.txt` | Python dependencies |
| `setup_admin_new.py` | Create admin user |
| `finance.db` | SQLite database (auto-created) |

## 🔧 Troubleshooting

### Issue 1: Port 8000 Already in Use

**Solution:**
```bash
# Use different port
uvicorn main:app --port 8001
```

### Issue 2: Import Errors

**Solution:**
```bash
# Reinstall dependencies
pip install --upgrade -r requirements_new.txt
```

### Issue 3: Database Locked

**Solution:**
```bash
# Remove database file and restart
del finance.db
python setup_admin_new.py
python main.py
```

### Issue 4: Secret Key Issues

**Solution:**
```bash
# Create proper .env file
copy .env.example .env

# Or set environment variable:
set SECRET_KEY=your-random-secret-key
```

## 🔄 Development Workflow

### 1. Feature Development

```bash
# Create branch
git checkout -b feature/new-feature

# Make changes
# Edit files...

# Test locally
pytest tests/ -v

# Push to repository
git push origin feature/new-feature
```

### 2. Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_api.py::test_login -v

# Run with coverage
pytest tests/ --cov=.
```

### 3. Code Quality

```bash
# Format code
black .

# Check style
flake8 .

# Type checking
mypy .
```

## 📚 Documentation Structure

```
docs/
├── README_NEW.md          ← Start here
├── SETUP_GUIDE.md         ← This file
├── ARCHITECTURE.md        ← Technical deep dive
├── API_REQUESTS.md        ← Sample requests
└── DATABASE_SCHEMA.md     ← Schema details
```

## 🚀 Deployment Preparation

### Before Going to Production

1. **Update Configuration**
   ```bash
   # Change SECRET_KEY
   SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
   
   # Set DEBUG=False
   # Use PostgreSQL instead of SQLite
   ```

2. **Security Checklist**
   - [ ] Change all default passwords
   - [ ] Update SECRET_KEY
   - [ ] Set DEBUG=False
   - [ ] Configure CORS properly
   - [ ] Enable HTTPS/SSL
   - [ ] Set secure headers
   - [ ] Add rate limiting
   - [ ] Configure logging

3. **Database Migration**
   ```bash
   # Create PostgreSQL database
   createdb finance_production
   
   # Update connection string
   DATABASE_URL=postgresql://user:pass@host:5432/finance_production
   ```

4. **Monitoring**
   - Set up logging
   - Monitor API performance
   - Track error rates
   - Setup alerts

## 📞 Support & Resources

### Documentation
- FastAPI: https://fastapi.tiangolo.com
- SQLAlchemy: https://www.sqlalchemy.org
- Pydantic: https://docs.pydantic.dev
- Python-Jose: https://github.com/mpdavis/python-jose

### Common Commands

```bash
# View logs
tail -f uvicorn.log

# Check database
sqlite3 finance.db ".tables"

# Create backup
cp finance.db finance.db.backup

# Reset database
rm finance.db
python setup_admin_new.py
```

## ✨ Next Steps

1. ✅ Complete setup
2. ✅ Test endpoints in Swagger UI
3. ✅ Review ARCHITECTURE.md
4. ✅ Try sample API requests
5. ✅ Create financial records
6. ✅ Test different user roles
7. ✅ Run test suite
8. ✅ Deploy to production

---

**For questions:** Review README_NEW.md and ARCHITECTURE.md

**Happy coding!** 🚀
