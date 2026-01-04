# Expense Tracker Application

## 📋 Project Overview

**Expense Tracker with Generative AI** is a production-ready web application that helps users track their income and expenses while leveraging artificial intelligence to automatically classify expenses and generate personalized financial insights.

### 🎯 Key Features

✅ **User Authentication**
- Secure registration and login
- Password hashing with Werkzeug
- Session-based authentication

✅ **Expense & Income Management**
- Add, view, edit, delete expenses and income
- Date-based categorization
- Category tracking

✅ **AI-Powered Features**
- Automatic expense classification using OpenAI API
- Intelligent prompt engineering for expense categorization
- AI-generated monthly financial insights and recommendations

✅ **Financial Analytics**
- Monthly summary dashboard
- Category-wise expense breakdown
- Income vs Expenses analysis
- Yearly financial trends
- Savings calculation

✅ **Modern UI/UX**
- Responsive dashboard design
- Interactive charts with Chart.js
- Real-time data updates
- Mobile-friendly interface

---

## 🏗️ System Architecture

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   Frontend (HTML/CSS/JS)                │
│         - Dashboard, Forms, Charts, Notifications       │
└────────────────────┬────────────────────────────────────┘
                     │ AJAX/Fetch Requests
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Flask Web Server                       │
│  ┌─────────────────────────────────────────────────┐   │
│  │        Routes / Blueprints                      │   │
│  │  - /api/auth/* (Authentication)                 │   │
│  │  - /api/expenses/* (Expense Management)         │   │
│  │  - /api/incomes/* (Income Management)           │   │
│  │  - /api/summary/* (Analytics & Insights)        │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │        Services Layer                           │   │
│  │  - LLMService (OpenAI Integration)              │   │
│  │  - Authentication Service                       │   │
│  │  - Validation & Utilities                       │   │
│  └─────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┬──────────────┐
        ▼                         ▼              ▼
    ┌────────────┐           ┌────────────┐  ┌──────────┐
    │  SQLite    │           │  OpenAI    │  │ External │
    │  Database  │           │   API      │  │  APIs    │
    └────────────┘           └────────────┘  └──────────┘
```

### Technology Stack

- **Backend**: Flask 2.3.3, Python 3.8+
- **Database**: SQLite (development) / PostgreSQL (production)
- **ORM**: SQLAlchemy
- **AI/LLM**: OpenAI API (GPT-3.5-turbo / GPT-4)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Charts**: Chart.js
- **Authentication**: Flask sessions with password hashing
- **API Style**: RESTful

---

## 📊 Database Schema

### User Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT NOW(),
    INDEX username,
    INDEX email
);
```

### Income Table
```sql
CREATE TABLE incomes (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL FOREIGN KEY,
    amount FLOAT NOT NULL,
    source VARCHAR(120) NOT NULL,
    date DATE NOT NULL,
    created_at DATETIME DEFAULT NOW(),
    INDEX user_id,
    INDEX date
);
```

### Expense Table
```sql
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL FOREIGN KEY,
    amount FLOAT NOT NULL,
    description VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    ai_classified BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT NOW(),
    INDEX user_id,
    INDEX date,
    INDEX category
);
```

### Relationships
- User → Income (1-to-Many)
- User → Expense (1-to-Many)
- All foreign keys have cascade delete

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- OpenAI API Key (free tier available)

### Step 1: Clone the Repository

```bash
cd /path/to/expenses_Tracker
```

### Step 2: Create Virtual Environment

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your OpenAI API key
# Get it from: https://platform.openai.com/api-keys
```

### Step 5: Initialize Database

```bash
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

### Step 6: Run the Application

```bash
python app.py
```

Visit: **http://localhost:5000**

---

## 📝 API Documentation

### Authentication Endpoints

#### Register User
```
POST /api/auth/register
Content-Type: application/json

{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepass123",
    "confirm_password": "securepass123"
}

Response (201):
{
    "success": true,
    "message": "Registration successful!",
    "user_id": 1
}
```

#### Login
```
POST /api/auth/login
Content-Type: application/json

{
    "username": "johndoe",
    "password": "securepass123"
}

Response (200):
{
    "success": true,
    "message": "Login successful",
    "user_id": 1,
    "username": "johndoe"
}
```

#### Logout
```
POST /api/auth/logout

Response (200):
{
    "success": true,
    "message": "Logout successful"
}
```

### Expense Endpoints

#### Add Expense (with AI Classification)
```
POST /api/expenses/add
Content-Type: application/json

{
    "amount": 45.50,
    "description": "Lunch at Italian restaurant",
    "category": "Food",           // Optional
    "date": "2024-01-15",         // Optional, defaults to today
    "ai_classify": true           // Optional, auto-classify if true
}

Response (201):
{
    "success": true,
    "message": "Expense added successfully",
    "expense": {
        "id": 1,
        "amount": 45.50,
        "description": "Lunch at Italian restaurant",
        "category": "Food",
        "date": "2024-01-15",
        "ai_classified": true,
        "created_at": "2024-01-15T10:30:00"
    }
}
```

#### Get Expenses
```
GET /api/expenses/list?month=1&year=2024&limit=50&offset=0

Response (200):
{
    "success": true,
    "total": 25,
    "count": 25,
    "expenses": [...]
}
```

#### AI Classify Expense
```
POST /api/expenses/classify
Content-Type: application/json

{
    "description": "Bought gasoline for car"
}

Response (200):
{
    "success": true,
    "category": "Travel"
}
```

### Income Endpoints

#### Add Income
```
POST /api/incomes/add
Content-Type: application/json

{
    "amount": 3000.00,
    "source": "Monthly Salary",
    "date": "2024-01-01"
}

Response (201):
{
    "success": true,
    "message": "Income added successfully",
    "income": {...}
}
```

#### Get Income
```
GET /api/incomes/list?month=1&year=2024&limit=50&offset=0

Response (200):
{
    "success": true,
    "total": 5,
    "count": 5,
    "incomes": [...]
}
```

### Summary & Insights Endpoints

#### Get Monthly Summary
```
GET /api/summary/monthly?month=1&year=2024

Response (200):
{
    "success": true,
    "month": 1,
    "year": 2024,
    "total_income": 3000.00,
    "total_expenses": 1500.00,
    "savings": 1500.00,
    "expenses_by_category": {
        "Food": 500.00,
        "Travel": 400.00,
        "Shopping": 600.00
    }
}
```

#### Get AI Insights
```
GET /api/summary/ai-insights?month=1&year=2024

Response (200):
{
    "success": true,
    "month": 1,
    "year": 2024,
    "summary": {...},
    "insights": "Based on your January spending..."
}
```

#### Get Yearly Summary
```
GET /api/summary/yearly?year=2024

Response (200):
{
    "success": true,
    "year": 2024,
    "total_income": 36000.00,
    "total_expenses": 18000.00,
    "savings": 18000.00,
    "monthly_breakdown": [...]
}
```

---

## 🤖 AI/LLM Integration

### Expense Classification Prompt Engineering

The system uses OpenAI's GPT-3.5-turbo to automatically classify expenses:

```python
prompt = """You are an intelligent finance assistant.
Classify the following expense into one category only:
Food, Travel, Shopping, Bills, Entertainment, Health, Other.

Expense description: {expense_description}

Return only the category name."""
```

**Example Classifications:**
- "Bought lunch at McDonald's" → **Food**
- "Uber ride to airport" → **Travel**
- "Netflix subscription" → **Entertainment**
- "Doctor appointment copay" → **Health**
- "Electricity bill payment" → **Bills**

### Monthly Insights Prompt Engineering

```python
prompt = """You are a personal finance advisor.

Based on the user's monthly expense data below, generate:
1. Total spending summary
2. Top 3 spending categories
3. Spending behavior analysis
4. 3 personalized money-saving tips

Expense Data:
{json_expense_data}

Keep the response concise, practical, and user-friendly."""
```

### Implementation Details

See [services/llm_service.py](services/llm_service.py):

```python
# Classification with fallback
try:
    category = llm_service.classify_expense("Restaurant meal")
    # Returns: "Food"
except APIError:
    category = "Other"  # Fallback
```

---

## 🔐 Security Features

✅ **Password Security**
- Werkzeug's `generate_password_hash()` for secure hashing
- bcrypt-based algorithm
- Unique per-user salts

✅ **Session Management**
- Secure HTTP-only cookies
- CSRF protection ready
- Session timeout (configurable)
- Automatic logout on browser close

✅ **Input Validation**
- Email format validation
- Amount positive number validation
- Date format validation
- String sanitization to prevent XSS

✅ **API Security**
- Authentication required for all protected routes
- User can only access their own data
- Proper HTTP status codes
- Error messages don't leak sensitive info

✅ **Environment Security**
- API keys stored in `.env` (not in code)
- `.env` excluded from git
- Production `SECRET_KEY` should be unique

---

## 📚 Project Structure

```
expenses_Tracker/
├── app.py                      # Main Flask application
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
│
├── models/
│   ├── __init__.py
│   └── models.py              # SQLAlchemy models (User, Income, Expense)
│
├── routes/
│   ├── __init__.py
│   ├── auth.py                # Authentication routes
│   ├── expenses.py            # Expense management routes
│   ├── income.py              # Income management routes
│   └── summary.py             # Analytics & insights routes
│
├── services/
│   ├── __init__.py
│   └── llm_service.py         # OpenAI API integration
│
├── utils/
│   ├── __init__.py
│   └── helpers.py             # Helper functions & validators
│
├── templates/
│   ├── dashboard.html         # Main dashboard
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   └── errors/
│       ├── 404.html
│       └── 500.html
│
└── static/
    ├── css/
    │   ├── auth.css           # Authentication page styles
    │   └── style.css          # Main application styles
    └── js/
        ├── app.js             # Utility functions
        └── dashboard.js       # Dashboard logic
```

---

## 🎓 Interview Explanation

### Question 1: "Tell me about this project"

**Answer:**
"This is a full-stack expense tracker web application that I built from scratch. It's designed to be production-ready and demonstrates several key concepts:

The backend is built with Flask and uses SQLAlchemy for database management. I implemented user authentication with secure password hashing, and created RESTful APIs for core operations like adding/managing expenses and income.

The interesting part is the AI integration - I use OpenAI's API to automatically classify expenses into categories and generate monthly financial insights. This involved careful prompt engineering to ensure accuracy and reliability.

For the frontend, I created a responsive dashboard with Chart.js visualizations, real-time data updates using JavaScript Fetch API, and a clean, modern UI.

The entire application follows MVC architecture with proper separation of concerns: models for database, routes for API endpoints, and services for business logic like LLM integration."

### Question 2: "How did you implement AI-powered expense classification?"

**Answer:**
"I created a dedicated LLMService class that handles all OpenAI API interactions. For expense classification, I engineered a specific prompt that:

1. Tells the model to act as a finance assistant
2. Provides the exact categories we support
3. Passes the expense description
4. Explicitly requests only the category name

The implementation includes error handling - if the API is unavailable, it falls back to 'Other' category. I also added validation to ensure the returned category matches our allowed list.

The prompt was iteratively tested with various inputs to achieve high accuracy. For example, 'Netflix subscription' correctly classifies as 'Entertainment', while 'Uber to airport' classifies as 'Travel'."

### Question 3: "What security measures did you implement?"

**Answer:**
"Security is built in at multiple layers:

1. **Authentication**: User passwords are hashed using Werkzeug's `generate_password_hash()` which uses bcrypt-based algorithms with unique salts per user.

2. **Session Management**: I use secure HTTP-only cookies with SAMESITE protection to prevent CSRF and XSS attacks. Sessions are tied to user IDs and authenticated on each protected request.

3. **Input Validation**: All user inputs are validated - emails checked for format, amounts for being positive numbers, dates validated against the required format.

4. **Data Isolation**: Each user can only access their own data through database queries filtered by `user_id`. This is enforced at the API level.

5. **API Keys**: Sensitive credentials like OpenAI API key are stored in `.env` environment variables, not hardcoded. The `.env` file is excluded from version control.

6. **Error Handling**: API errors don't leak sensitive information - they return generic messages while logging details internally."

### Question 4: "How would you scale this application?"

**Answer:**
"Good question. For scaling, I would:

1. **Database**: Switch from SQLite to PostgreSQL for concurrent write operations and better performance at scale.

2. **Caching**: Implement Redis for caching frequently accessed data like monthly summaries, reducing database hits.

3. **Async Processing**: Use Celery for long-running operations like AI insight generation, preventing request timeouts.

4. **Load Balancing**: Deploy multiple Flask instances behind Nginx with load balancing.

5. **API Rate Limiting**: Implement rate limiting on both expense classification and insight generation to control OpenAI API costs.

6. **Monitoring**: Add logging and monitoring with services like Sentry and DataDog to track errors in production.

7. **Frontend Optimization**: Implement code splitting, lazy loading, and PWA features for better performance on mobile."

### Question 5: "What would you add as next features?"

**Answer:**
"Several features would enhance the app:

1. **Budget Tracking**: Set monthly budgets per category with alerts when approaching limits.

2. **Recurring Expenses**: Handle recurring bills automatically.

3. **CSV Export**: Export monthly/yearly data for external analysis.

4. **Multiple Currencies**: Support different currencies with real-time conversion rates.

5. **Spending Trends**: ML-powered prediction of future spending patterns.

6. **Bill Reminders**: Push notifications for upcoming bills.

7. **Social Features**: Compare spending patterns with anonymized averages.

8. **Mobile App**: Native iOS/Android app with offline support.

9. **Advanced Analytics**: Tax category insights, retirement savings projections.

10. **Custom LLM Prompts**: Allow users to customize AI insight generation."

---

## 🧪 Testing

### Manual Testing

```bash
# Test Registration
POST http://localhost:5000/api/auth/register
{
    "username": "testuser",
    "email": "test@example.com",
    "password": "test123456",
    "confirm_password": "test123456"
}

# Test Login
POST http://localhost:5000/api/auth/login
{
    "username": "testuser",
    "password": "test123456"
}

# Test Add Expense with AI Classification
POST http://localhost:5000/api/expenses/add
{
    "amount": 50,
    "description": "Bought groceries at Whole Foods",
    "date": "2024-01-15",
    "ai_classify": true
}

# Test Get Summary
GET http://localhost:5000/api/summary/monthly?month=1&year=2024

# Test AI Insights
GET http://localhost:5000/api/summary/ai-insights?month=1&year=2024
```

---

## 📦 Deployment

### Deploy to Heroku

```bash
# Create Procfile
echo "web: gunicorn app:app" > Procfile

# Create runtime.txt
echo "python-3.11.0" > runtime.txt

# Install Gunicorn
pip install gunicorn

# Deploy
heroku create your-app-name
heroku config:set OPENAI_API_KEY=your-key-here
git push heroku main
```

### Deploy to AWS (EC2)

```bash
# SSH into instance
ssh -i key.pem ec2-user@your-instance

# Clone repo and setup
git clone <repo>
cd expenses_Tracker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 📄 License

This project is open source and available under the MIT License.

---

## 👨‍💻 Author

**Aditya** - Full-Stack Python & AI Developer

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

---

## 📞 Support

For issues and questions:
- Check the documentation above
- Review existing issues on GitHub
- Create a new issue if needed

---

## 🎯 Project Goals Achieved

✅ Production-ready code with proper architecture
✅ User authentication with secure password handling
✅ RESTful API with proper error handling
✅ AI-powered expense classification using OpenAI API
✅ Advanced prompt engineering for insights
✅ Responsive, modern UI with real-time updates
✅ Database design with proper relationships
✅ Security best practices implemented
✅ Comprehensive documentation
✅ Interview-ready project with clear explanations

---

**Version:** 1.0.0  
**Last Updated:** January 2024  
**Status:** Production Ready ✨
