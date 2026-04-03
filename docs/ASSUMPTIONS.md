# Project Assumptions & Decisions

## 📋 Assumptions Made

### 1. Database & Persistence
**Assumption:** SQLite is sufficient for interview purposes
- ✅ Portable, no setup required
- ✅ Works perfectly for demonstration
- ❌ Not suitable for production with multiple servers
**Reality Check:** Production would use PostgreSQL with connection pooling

### 2. Authentication Scope
**Assumption:** No logout blacklist needed
- ✅ Stateless JWT is simpler
- ✅ Tokens expire automatically
- ❌ User can't be logged out immediately
**Reality Check:** Production would have token blacklist with Redis

### 3. Financial Records Ownership
**Assumption:** Users only see their own records
- ✅ Simpler business logic
- ✅ Clear permission model
- ❌ Analysts can't see cross-user analytics by default
**Reality Check:** Analysts would need special permissions to view others' data

### 4. Category Management
**Assumption:** Categories are free-form strings
- ✅ More flexible for users
- ✅ No predefined list needed
- ❌ No consistency across categories
**Reality Check:** Production might have a category master list

### 5. Financial Amounts
**Assumption:** Amounts are always positive, with type (income/expense) determining sign
- ✅ Simpler validation
- ✅ Prevents "negative income" confusion
- ❌ Requires client-side logic for display
**Reality Check:** Alternative: store signed amounts with positive/negative values

### 6. Date Fields
**Assumption:** Date defaults to current UTC time if not provided
- ✅ Convenience for users
- ✅ Automatic timestamps
- ❌ Timezone considerations
**Reality Check:** Production would handle timezone preferences per user

### 7. Token Expiration
**Assumption:** Access token = 30 minutes, Refresh = 7 days
- ✅ Common industry standard
- ✅ Balances security and convenience
- ❌ Not configurable per deployment
**Reality Check:** Would make configurable in production

### 8. Role Permissions
**Assumption:** Fixed three-tier role model
- ✅ Simple, clear hierarchy
- ✅ Easy to implement and test
- ❌ Not flexible for custom permissions
**Reality Check:** Enterprise systems would use RBAC with permission matrix

### 9. Password Hashing
**Assumption:** Bcrypt is sufficient
- ✅ Industry standard, secure by default
- ✅ Handles salt automatically
- ❌ Slower than required for some high-throughput scenarios
**Reality Check:** Bcrypt is fine; alternatives like Argon2 for extreme security needs

### 10. API Versioning
**Assumption:** Use `/api/v1/` prefix
- ✅ Allows future API changes
- ✅ Backward compatibility path
- ❌ Requires coordination when updating
**Reality Check:** Necessary for production APIs

## ⚠️ Trade-offs Made

### Architecture vs. Simplicity

**Chose:** Clean Layered Architecture
```
✅ Pros:
  - Testable
  - Maintainable
  - Scalable
  - Industry standard

❌ Cons:
  - More files
  - Learning curve
  - Slightly more boilerplate
```

**Alternative:** Everything in routes
```
✅ Pros:
  - Fewer files
  - Faster to write
  - Simpler to understand initially

❌ Cons:
  - Hard to test
  - Difficult to reuse logic
  - Becomes spaghetti code
```

### Database Complexity vs. Features

**Chose:** Simple SQLite
```
✅ Pros:
  - No setup
  - Portable
  - Good for learning

❌ Cons:
  - Can't scale to multiple servers
  - Slower with many concurrent requests
```

**Alternative:** PostgreSQL
```
✅ Pros:
  - Production-ready
  - Better performance
  - Advanced features

❌ Cons:
  - Requires setup
  - Needs production deployment
```

### Authentication Method

**Chose:** JWT Tokens
```
✅ Pros:
  - Stateless
  - Scalable
  - Mobile-friendly

❌ Cons:
  - Can't revoke immediately
  - Larger token size
  - Needs refresh logic
```

**Alternative:** Session-based (cookies)
```
✅ Pros:
  - Can revoke immediately
  - Smaller payload
  - Simpler initially

❌ Cons:
  - Server must store sessions
  - Doesn't scale horizontally
  - CORS issues
```

## 🎯 Design Decisions Rationale

### 1. Why Pydantic for Validation?

**Decision:** Use Pydantic schemas instead of manual validation

**Rationale:**
- Auto-generates OpenAPI documentation
- Type checking and IDE support
- Reusable across endpoints
- Built-in validation rules
- Custom validators supported

### 2. Why Separate Services Layer?

**Decision:** Create service classes separate from routes

**Rationale:**
- Testable without HTTP context
- Reusable across multiple endpoints
- Clear business logic boundary
- Easier to debug
- Can be called from other services

### 3. Why Decorator-Based RBAC?

**Decision:** Use decorators for permission checking

**Rationale:**
- Declarative and clear
- Single source of truth for permissions
- Reusable across routes
- Easy to audit
- Type-safe (IDE support)

### 4. Why ORM Over Raw SQL?

**Decision:** Use SQLAlchemy ORM instead of raw SQL

**Rationale:**
- SQL injection prevention
- Database agnostic (switch DB easily)
- Relationship management
- Query builder
- Type safety

### 5. Why Pagination Over Single Endpoint?

**Decision:** Implement pagination with skip/limit

**Rationale:**
- Prevents loading millions of records
- Better API performance
- User-friendly
- Industry standard
- Easy to implement on frontend

## 📊 Comparison with Alternatives

### Framework Choice: FastAPI vs. Alternatives

| Feature | FastAPI | Flask | Django | Express.js |
|---------|:-------:|:-----:|:------:|:----------:|
| Speed | ⚡⚡⚡ | ⚡ | ⚡ | ⚡⚡⚡ |
| Docs | Auto | Manual | Manual | Manual |
| Learning | Easy | Very Easy | Hard | Medium |
| Features | Basic | Basic | Full | Basic |
| Validation | Pydantic | Manual | Django ORM | Manual |
| Type Safety | ✅ | ❌ | Partial | ❌ |

**Why FastAPI?** Modern, fast, excellent documentation, great for APIs

### Database: SQLite vs. PostgreSQL

| Aspect | SQLite | PostgreSQL |
|--------|:------:|:----------:|
| Setup | None | Requires install |
| Portability | ✅ | ❌ |
| Performance | Good | Excellent |
| Scaling | Single server | Multiple servers |
| Features | Basic | Advanced |
| For Interview | ✅ | ❌ |
| For Production | ❌ | ✅ |

**Why SQLite?** For interview; easy migration to PostgreSQL

### ORM: SQLAlchemy vs. Alternatives

| Feature | SQLAlchemy | Django ORM | Tortoise | Pony |
|---------|:----------:|:----------:|:--------:|:----:|
| Database Agnostic | ✅ | ✅ | Partial | ✅ |
| Relationships | ✅ | ✅ | ✅ | ✅ |
| Query Builder | ✅ | ✅ | ✅ | ✅ |
| Standalone | ✅ | ❌ | ✅ | ✅ |
| Documentation | Excellent | Good | Good | Good |

**Why SQLAlchemy?** Works with FastAPI, database agnostic, excellent documentation

## 🔄 Future Improvements

### Short Term (Weeks 1-2)
- [ ] Add Redis caching for dashboard
- [ ] Implement rate limiting
- [ ] Add more comprehensive tests
- [ ] Setup CI/CD pipeline
- [ ] Add request logging

### Medium Term (Months 1-2)
- [ ] Migrate to PostgreSQL
- [ ] Add token blacklist
- [ ] Implement bulk import
- [ ] Add file exports (CSV, PDF)
- [ ] Setup monitoring & alerts

### Long Term (Months 3+)
- [ ] Multi-user dashboards
- [ ] Budget planning features
- [ ] Recurring transactions
- [ ] Receipt image storage
- [ ] Mobile app
- [ ] AI-powered insights

## 💡 Key Learnings

### What Worked Well
1. ✅ Layered architecture kept code organized
2. ✅ Pydantic validation reduced bugs
3. ✅ JWT authentication was straightforward
4. ✅ FastAPI's dependency injection was elegant
5. ✅ SQLAlchemy made database changes easy

### Challenges Overcome
1. ❌ → ✅ Initial JWT complexity → Simplified with service layer
2. ❌ → ✅ RBAC complexity → Solved with decorators
3. ❌ → ✅ Validation duplication → Solved with Pydantic
4. ❌ → ✅ Testing complexity → Solved with separation of concerns

### What I'd Do Differently
1. Start with PostgreSQL from day 1 (for production features)
2. Add caching layer earlier (for performance insight)
3. Implement logging from start (for debugging)
4. Add rate limiting earlier (for security)

## 🧠 Interview Insights

### Questions to Expect
1. "How would you add feature X?"
2. "What if requirements changed to Y?"
3. "How would you optimize for Z?"
4. "What about edge case W?"

### How to Approach
1. **Acknowledge** the question
2. **Think out loud** - show your process
3. **Propose solution** with trade-offs
4. **Ask clarifying questions** - show you think through requirements
5. **Reference your code** - connect to what you built

### What Impresses Interviewers
- ✅ Understanding your own code deeply
- ✅ Thinking through trade-offs
- ✅ Asking clarifying questions
- ✅ Clean code and organization
- ✅ Production-ready thinking
- ✅ Knowledge of alternatives
- ✅ Willingness to learn

## 📚 Documentation Index

| Document | Purpose | Length |
|----------|---------|--------|
| `README_NEW.md` | Project overview & features | 5 min read |
| `SETUP_GUIDE.md` | Installation & running | 10 min read |
| `ARCHITECTURE.md` | Technical deep dive | 15 min read |
| `API_REQUESTS.md` | Sample API calls | 10 min read |
| `INTERVIEW_GUIDE.md` | Presentation guide | 20 min read |
| `ASSUMPTIONS.md` | This document | 10 min read |

## ✨ Summary

This project demonstrates:
- ✅ Clean, production-quality code
- ✅ Proper separation of concerns
- ✅ Industry-standard architecture
- ✅ Comprehensive API design
- ✅ Role-based access control
- ✅ Security best practices
- ✅ Testable code structure
- ✅ Professional documentation

**Perfect for:** Backend developer positions, interviews, portfolio showcase

---

**Last Updated:** 2024
**Version:** 1.0.0
