# Technical Architecture Document

## System Overview

```
┌────────────────────────────────────────────────────────────────┐
│                      USER BROWSER                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │             Frontend (HTML/CSS/JavaScript)               │  │
│  │  - Dashboard.html (main interface)                       │  │
│  │  - Auth pages (login/register)                           │  │
│  │  - Chart.js for visualizations                           │  │
│  │  - Real-time data fetch with Fetch API                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────┬──────────────────────────────────────┘
                          │
                   HTTP/HTTPS (Ajax)
                          │
┌─────────────────────────▼──────────────────────────────────────┐
│                    FLASK SERVER                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │            Routes (Blueprints)                           │  │
│  │  ┌─ /api/auth/* ────── Authentication (register, login) │  │
│  │  ├─ /api/expenses/* ─ Expense CRUD + AI classification  │  │
│  │  ├─ /api/incomes/* ── Income CRUD                       │  │
│  │  └─ /api/summary/* ─ Analytics & AI insights            │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           Services & Business Logic                      │  │
│  │  ┌─ LLMService: OpenAI API integration                   │  │
│  │  ├─ Helpers: Validation, formatting                     │  │
│  │  └─ Config: Environment-based settings                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Models (SQLAlchemy ORM)                          │  │
│  │  ├─ User (authentication, relationships)                │  │
│  │  ├─ Income (income tracking)                            │  │
│  │  └─ Expense (expense tracking, AI classification)       │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────┬──────────────────────────┬────────────────────────┘
             │                          │
      Database API               External API
             │                          │
┌────────────▼──────────────┐  ┌────────▼──────────────────────┐
│    SQLite Database        │  │   OpenAI API                  │
│  (Development)            │  │  - GPT-3.5-turbo              │
│  PostgreSQL (Production)  │  │  - Expense classification     │
│                           │  │  - Insight generation         │
│  Tables:                  │  │                               │
│  - users                  │  │ Endpoints:                    │
│  - incomes                │  │ POST /chat/completions        │
│  - expenses               │  │                               │
└───────────────────────────┘  └───────────────────────────────┘
```

## Request Flow - Adding an Expense

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. User enters expense data in dashboard.html                   │
│    - Amount: 45.50                                              │
│    - Description: "Lunch at Italian restaurant"                 │
│    - Category: [empty - will use AI]                            │
│    - Date: 2024-01-15                                           │
└──────────────┬──────────────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────────────┐
│ 2. JavaScript validates input (app.js)                          │
│    - Amount > 0? ✓                                              │
│    - Description not empty? ✓                                   │
│    - Date valid format? ✓                                       │
└──────────────┬──────────────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────────────┐
│ 3. POST /api/expenses/add with JSON body (Fetch API)            │
│    {                                                             │
│      "amount": 45.50,                                           │
│      "description": "Lunch at Italian restaurant",              │
│      "category": null,                                          │
│      "date": "2024-01-15",                                      │
│      "ai_classify": true                                        │
│    }                                                             │
└──────────────┬──────────────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────────────┐
│ 4. Flask route handler (routes/expenses.py)                     │
│    - Authenticate user (check session['user_id'])               │
│    - Validate input data                                        │
│    - Check if ai_classify == True                               │
└──────────────┬──────────────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────────────┐
│ 5. Call LLMService.classify_expense()                           │
│    - Build prompt:                                              │
│      "You are a finance assistant..."                           │
│      "Classify: Lunch at Italian restaurant"                    │
│    - Call OpenAI API                                            │
│    - Get response: "Food"                                       │
│    - Validate against allowed categories                        │
└──────────────┬──────────────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────────────┐
│ 6. Create Expense model & save to database                      │
│    expense = Expense(                                           │
│      user_id=1,                                                 │
│      amount=45.50,                                              │
│      description="Lunch at Italian restaurant",                 │
│      category="Food",                                           │
│      date=date(2024, 1, 15),                                    │
│      ai_classified=True                                         │
│    )                                                             │
│    db.session.add(expense)                                      │
│    db.session.commit()                                          │
└──────────────┬──────────────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────────────┐
│ 7. Return JSON response                                         │
│    {                                                             │
│      "success": true,                                           │
│      "message": "Expense added successfully",                   │
│      "expense": {                                               │
│        "id": 123,                                               │
│        "amount": 45.50,                                         │
│        "description": "Lunch at Italian restaurant",            │
│        "category": "Food",                                      │
│        "date": "2024-01-15",                                    │
│        "ai_classified": true,                                   │
│        "created_at": "2024-01-15T10:30:00"                      │
│      }                                                           │
│    }                                                             │
└──────────────┬──────────────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────────────┐
│ 8. JavaScript receives response (dashboard.js)                  │
│    - Show success notification                                  │
│    - Clear form                                                 │
│    - Reload expenses list                                       │
│    - Update dashboard summary                                   │
│    - Refresh category chart                                     │
└──────────────────────────────────────────────────────────────────┘
```

## Data Flow - Generating AI Insights

```
User Requests Insights (January 2024)
           │
           ▼
Get Monthly Summary (SQL aggregation)
   - Total Income: $3000
   - Total Expenses: $1500
   - By Category: Food: $500, Travel: $400...
           │
           ▼
Prepare JSON for LLM
{
  "month": "January",
  "year": 2024,
  "total_income": 3000,
  "total_expenses": 1500,
  "expenses_by_category": {...}
}
           │
           ▼
Build Prompt (LLMService)
"You are a personal finance advisor.
Based on the user's expense data: {...}
Generate: 1. Summary, 2. Top categories,
3. Behavior analysis, 4. Money-saving tips"
           │
           ▼
Call OpenAI API (requests library)
Headers: {"Authorization": "Bearer sk-..."}
Body: {model: "gpt-3.5-turbo", messages: [...]}
           │
           ▼
Receive & Parse Response
"Your spending shows a healthy 50% savings rate.
Top categories: Food ($500), Travel ($400)..."
           │
           ▼
Return to Frontend
Display in insights section
```

## Security Layers

```
Frontend Security
├─ Input validation before sending
├─ XSS prevention (HTML escaping)
├─ CSRF token in forms
└─ LocalStorage for non-sensitive data

Network Security
├─ HTTPS in production
├─ Secure cookies (HTTP-only, SAMESITE)
├─ CORS headers configured
└─ Rate limiting on sensitive endpoints

Backend Security
├─ Session validation on protected routes
├─ Input validation (types, lengths, formats)
├─ SQL injection prevention (SQLAlchemy ORM)
├─ Authentication decorator on routes
└─ Error messages don't leak info

Database Security
├─ Password hashing (bcrypt)
├─ Foreign key constraints
├─ User data isolation (user_id in queries)
├─ Transactions for data integrity
└─ Prepared statements (ORM)

Configuration Security
├─ Environment variables for secrets
├─ Config objects for settings
├─ .env.example for documentation
├─ .gitignore excludes sensitive files
└─ Different configs per environment
```

## API Endpoint Structure

```
/api/auth/
├─ POST   /register          (Create user account)
├─ POST   /login             (Authenticate user)
├─ POST   /logout            (End session)
├─ GET    /profile           (User info)
└─ GET    /check-session     (Session status)

/api/expenses/
├─ POST   /add               (Create expense with optional AI classification)
├─ GET    /list              (Get expenses with filters)
├─ GET    /:id               (Get single expense)
├─ PUT    /:id               (Update expense)
├─ DELETE /:id               (Delete expense)
└─ POST   /classify          (AI classify text)

/api/incomes/
├─ POST   /add               (Create income)
├─ GET    /list              (Get incomes)
├─ GET    /:id               (Get single income)
├─ PUT    /:id               (Update income)
└─ DELETE /:id               (Delete income)

/api/summary/
├─ GET    /monthly           (Monthly summary & breakdown)
├─ GET    /yearly            (Yearly summary with monthly breakdown)
├─ GET    /ai-insights       (AI-generated insights)
└─ POST   /budget            (Set & track budgets)
```

## Database Schema

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_username (username),
    INDEX idx_email (email)
);

CREATE TABLE incomes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount FLOAT NOT NULL CHECK (amount > 0),
    source VARCHAR(120) NOT NULL,
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_date (date)
);

CREATE TABLE expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount FLOAT NOT NULL CHECK (amount > 0),
    description VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    ai_classified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_category (category),
    INDEX idx_date (date)
);
```

## LLM Integration Details

### Expense Classification Flow

```
User Input: "Bought groceries at Whole Foods"
                    │
                    ▼
            Validate Input
          (not empty, < 500 chars)
                    │
                    ▼
        Build Classification Prompt
"You are an intelligent finance assistant.
Classify the following expense into one 
category only: Food, Travel, Shopping, Bills,
Entertainment, Health, Other.

Expense description: Bought groceries at Whole Foods

Return only the category name."
                    │
                    ▼
    Call OpenAI API with GPT-3.5-turbo
    Temperature: 0.7 (balanced)
    Max tokens: 50
                    │
                    ▼
          Parse Response: "Food"
                    │
                    ▼
      Validate (is in allowed categories?)
         Yes → Return "Food"
         No → Return "Other" (fallback)
                    │
                    ▼
       Store category with expense
    ai_classified = True
```

### Monthly Insights Generation Flow

```
User Requests Insights for January 2024
                    │
                    ▼
    Get Monthly Aggregated Data
    SELECT SUM(amount), category FROM expenses
    WHERE user_id=1 AND month(date)=1 AND year(date)=2024
    GROUP BY category
    
    Results:
    {
      "total_income": 3000,
      "total_expenses": 1500,
      "expenses_by_category": {
        "Food": 500,
        "Travel": 400,
        "Shopping": 600
      }
    }
                    │
                    ▼
        Build Insights Prompt
"You are a personal finance advisor.
Based on the user's monthly expense data:
{JSON_DATA}

Generate:
1. Total spending summary
2. Top 3 spending categories
3. Spending behavior analysis
4. 3 personalized money-saving tips

Keep response concise and practical."
                    │
                    ▼
    Call OpenAI API with GPT-3.5-turbo
    Temperature: 0.7
    Max tokens: 500
                    │
                    ▼
      Receive AI Response
"Your January spending shows a healthy
pattern. You saved 50% of income.

Top Categories:
1. Shopping ($600)
2. Food ($500)
3. Travel ($400)

Analysis: Discretionary spending is your
largest area. Consider setting a weekly
shopping budget.

Tips:
1. Use cashback apps for online purchases
2. Meal prep to reduce food costs
3. Use public transport 2x weekly"
                    │
                    ▼
    Return to Frontend
    Display in insights section
```

## Performance Optimizations

```
Database Level
├─ Indexes on frequently queried columns
│  ├─ user_id (foreign key lookups)
│  ├─ date (range queries)
│  └─ category (filtering)
├─ Aggregation at DB level (SUM, COUNT, AVG)
├─ Connection pooling
└─ Query optimization with EXPLAIN

Application Level
├─ Pagination (50 records per page)
├─ Selective column queries
├─ Caching decorator ready
├─ Lazy loading relationships
└─ Request validation early

Frontend Level
├─ Chart.js lazy initialization
├─ Event delegation for lists
├─ Debouncing for search
└─ Image optimization

API Level
├─ Response compression
├─ Minimal JSON response
├─ Rate limiting (future)
└─ Caching headers set
```

## Testing Strategy

```
Unit Tests
├─ Helper functions (validate_email, validate_amount)
├─ Model methods (set_password, check_password)
└─ Date calculations

Integration Tests
├─ Auth flow (register → login → logout)
├─ Expense CRUD (create, read, update, delete)
├─ Income operations
└─ Summary calculations

API Tests
├─ Request/response validation
├─ Error handling (404, 500, 400)
├─ Authentication requirements
└─ Data isolation (user A can't see user B's data)

Manual Testing
├─ UI responsiveness on different devices
├─ AI classification accuracy
├─ Data persistence
└─ Error messages clarity
```

## Deployment Checklist

```
Pre-Deployment
☐ Set FLASK_ENV=production
☐ Generate strong SECRET_KEY
☐ Configure DATABASE_URL to PostgreSQL
☐ Set OPENAI_API_KEY
☐ Enable HTTPS only
☐ Set secure cookie flags
☐ Configure CORS properly
☐ Set up monitoring/logging

Deployment
☐ Use Gunicorn (not Flask dev server)
☐ Use Nginx as reverse proxy
☐ Set up SSL certificate
☐ Configure firewall
☐ Set up database backups
☐ Create admin user
☐ Test all features in production

Post-Deployment
☐ Monitor error logs
☐ Check API health
☐ Verify database connectivity
☐ Test email notifications (if added)
☐ Monitor API rate limits
☐ Check OpenAI API usage
☐ Set up automated backups
```

---

**This architecture is designed for:**
- ✓ Scalability (can handle 1000s of concurrent users)
- ✓ Security (multiple layers of protection)
- ✓ Maintainability (clean separation of concerns)
- ✓ Reliability (error handling and fallbacks)
- ✓ Performance (optimized queries and caching)
