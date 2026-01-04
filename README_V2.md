# 🎯 AI-Powered Expense Tracker with Automatic Transaction Detection

**Version:** 2.0.0 | **Status:** Production-Ready | **Date:** January 2024

A complete, production-ready expense tracking web application with **AI-powered automatic transaction detection from SMS/bank alerts**.

---

## 🚀 Key Features

### 📱 **NEW! Automatic Transaction Detection**
- Paste bank SMS alerts and transaction messages
- AI automatically extracts: amount, merchant, category, type
- Auto-updates balance (credit/debit)
- Prevents duplicate entries using SHA256 hash
- Edit or delete auto-detected transactions
- Compare auto vs manual entries

### 💰 **Complete Expense Tracking**
- Add/edit/delete income and expenses
- Categorize transactions (Food, Travel, Shopping, Bills, Entertainment, Health)
- Monthly summaries with charts
- Category breakdown analytics
- Savings calculation

### 🤖 **AI-Powered Intelligence**
- **Auto-Classification**: AI classifies expenses into categories
- **Message Parsing**: Extracts transaction details from alerts
- **Monthly Insights**: Personalized spending analysis and tips
- **Spending Advice**: Category-specific money-saving recommendations

### 💳 **Balance Management**
- Real-time balance tracking
- Automatic credit/debit updates
- Total credits and debits summary
- Historical transaction tracking
- Statistics (auto vs manual breakdown)

### 📊 **Analytics & Reporting**
- Interactive charts with Chart.js
- Monthly trend analysis
- Category-wise expense breakdown
- Income vs expense comparison
- Customizable date filters

### 🔐 **Security & Privacy**
- Secure user authentication with bcrypt
- Session-based authorization
- User data isolation
- No raw message storage
- API key management via environment variables

---

## 💻 Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Backend** | Flask | 2.3.3 |
| **Database** | SQLAlchemy + SQLite | 2.0.21 |
| **Frontend** | HTML5 + CSS3 + Vanilla JS | - |
| **Charts** | Chart.js | Latest |
| **AI/LLM** | OpenAI GPT-3.5-turbo | - |
| **Auth** | Werkzeug (bcrypt) | 2.3.7 |
| **Language** | Python | 3.8+ |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Browser (Frontend)                      │
│  HTML Dashboard + CSS Styling + JavaScript Interactivity    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ REST API
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Flask Application (Backend)                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Auth Routes │  │ Transaction  │  │ Expense Routes│    │
│  │              │  │ Message API  │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  LLM Service (OpenAI Integration)                   │  │
│  │  - Message Parsing                                  │  │
│  │  - Expense Classification                           │  │
│  │  - Insight Generation                               │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────┬─────────────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
   ┌─────────┐      ┌──────────────┐
   │SQLDatabase│      │OpenAI API    │
   │(SQLAlchemy)     │(GPT-3.5)     │
   └─────────┘      └──────────────┘
```

---

## 📦 Database Schema

### Tables

**Users**
```
id | username | email | password_hash | created_at
```

**UserBalance** (NEW!)
```
id | user_id | current_balance | total_credits | total_debits | last_updated
```

**Expenses**
```
id | user_id | amount | description | category | date | 
is_auto_detected | transaction_type | merchant_or_source | message_hash | created_at
```

**Income**
```
id | user_id | amount | source | date | created_at
```

**Transactions** (NEW!)
```
id | user_id | message_text | message_hash | transaction_type | amount | 
merchant_or_source | category | processing_status | raw_llm_response | created_at
```

---

## 🎮 User Interface

### Dashboard Sections

1. **📊 Overview**
   - Income, Expenses, Savings cards
   - Category breakdown chart
   - Month selector

2. **📱 Messages** (NEW!)
   - Paste transaction alerts
   - Auto-detected transactions list
   - Current balance display
   - Auto vs manual statistics

3. **💸 Expenses**
   - Add/edit/delete expenses
   - AI auto-classification
   - Transaction list

4. **💵 Income**
   - Add/edit/delete income
   - Multiple income sources

5. **🤖 AI Insights**
   - Monthly spending analysis
   - Personalized tips
   - Behavioral insights

6. **📈 Analytics**
   - Trend charts
   - Comparison graphs

---

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - Create account
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/profile` - Get user profile

### Transactions (NEW!)
- `POST /api/transactions/upload-message` - Process message
- `GET /api/transactions/auto` - Get auto transactions
- `PUT /api/transactions/{id}` - Edit transaction
- `DELETE /api/transactions/{id}` - Delete transaction
- `GET /api/balance/current` - Get balance
- `GET /api/balance/statistics` - Get statistics

### Expenses
- `POST /api/expenses/add` - Add expense
- `GET /api/expenses/list` - List expenses
- `PUT /api/expenses/{id}` - Edit expense
- `DELETE /api/expenses/{id}` - Delete expense

### Income
- `POST /api/incomes/add` - Add income
- `GET /api/incomes/list` - List income
- `PUT /api/incomes/{id}` - Edit income
- `DELETE /api/incomes/{id}` - Delete income

### Summary
- `GET /api/summary/monthly` - Monthly summary
- `GET /api/summary/yearly` - Yearly summary
- `GET /api/summary/ai-insights` - AI insights

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone and navigate
cd expenses_Tracker

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 2. Initialize Database

```bash
# Create tables
python3 -c "from app import app; from models.models import db; \
    db.init_app(app); app.app_context().push(); db.create_all()"
```

### 3. Run Application

```bash
python3 app.py
```

Visit: **http://localhost:5000**

### 4. Test Features

```bash
# Register account
# Test expense tracking
# Paste sample message: "₹2,500 debited from your account via UPI at Amazon"
# Verify auto-detection and balance update
```

---

## 💬 Example Transaction Messages

### Supported Formats

**UPI Debit:**
```
₹2,500 debited from your account via UPI at Amazon
```

**Card Purchase:**
```
Card ending in 1234 debited ₹5,000 at Flipkart
```

**Salary Credit:**
```
₹50,000 credited to your account. Salary received
```

**Refund:**
```
₹1,500 refunded from Amazon to your account
```

**Utility Bill:**
```
Electricity bill payment of ₹2,000 processed successfully
```

---

## 🤖 AI Features

### LLM Prompt Engineering

**Transaction Parsing:**
```
System: "You are a financial transaction parser."

Extract:
- transaction_type (Debit/Credit)
- amount (number only)
- merchant_or_source
- expense_category (Food, Travel, Shopping, Bills, Entertainment, Health, Other)

Return JSON format only.
```

**Monthly Insights:**
```
Analyze user's financial data and generate:
1. Total spending summary
2. Top 3 spending categories
3. Spending behavior analysis
4. 3 personalized money-saving tips

Keep advice practical and beginner-friendly.
```

---

## 🔐 Security Features

✅ **Password Security:** Bcrypt hashing with 100k+ iterations  
✅ **Session Management:** HTTP-only secure cookies  
✅ **User Isolation:** All queries filtered by user_id  
✅ **Duplicate Prevention:** SHA256 message hash  
✅ **Input Validation:** Message length, amount checks  
✅ **SQL Injection Prevention:** SQLAlchemy ORM  
✅ **XSS Prevention:** HTML escaping in templates  
✅ **Environment Variables:** API keys in .env  

---

## 📈 Automatic Balance Logic

```
IF transaction_type == "Debit":
    balance -= amount
    total_debits += amount
    
ELSE IF transaction_type == "Credit":
    balance += amount
    total_credits += amount

Update UserBalance table immediately
Create Expense/Income record with auto_detected=True
```

### Example

```
Starting: ₹50,000
+ Salary (₹5,000) = ₹55,000
- Shopping (₹2,500) = ₹52,500
- Bills (₹1,000) = ₹51,500
Final: ₹51,500
```

---

## 📁 Project Structure

```
expenses_Tracker/
├── app.py                      # Main Flask app
├── config.py                   # Configuration
├── requirements.txt            # Dependencies
├── .env.example               # Environment template
│
├── models/
│   ├── __init__.py
│   └── models.py              # Database models
│
├── routes/
│   ├── __init__.py
│   ├── auth.py                # Authentication
│   ├── expenses.py            # Expense CRUD
│   ├── income.py              # Income CRUD
│   ├── summary.py             # Analytics
│   └── transactions.py        # Message processing (NEW!)
│
├── services/
│   ├── __init__.py
│   ├── llm_service.py         # OpenAI integration
│   └── transaction_service.py # Message parsing (NEW!)
│
├── utils/
│   ├── __init__.py
│   └── helpers.py             # Validators, decorators
│
├── templates/
│   ├── dashboard.html         # Main dashboard
│   ├── index.html             # Home page
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   └── errors/
│       ├── 404.html
│       └── 500.html
│
└── static/
    ├── css/
    │   ├── style.css          # Main styles
    │   └── auth.css           # Auth styles
    └── js/
        ├── app.js             # Utilities
        ├── dashboard.js       # Dashboard logic
        └── transactions.js    # Message handling (NEW!)
```

---

## 🧪 Testing

### Manual Testing

```bash
# Test auto-detection
1. Navigate to "Messages" section
2. Paste: "₹2,500 debited from Amazon"
3. Verify parsing works
4. Check balance updated
5. Edit transaction
6. Delete transaction
7. Verify balance reversed

# Test statistics
1. Add multiple transactions
2. Check "Auto vs Manual" counts
3. Verify totals match
```

### API Testing

```bash
# Test message processing
curl -X POST http://localhost:5000/api/transactions/upload-message \
  -H "Content-Type: application/json" \
  -d '{"message":"₹2500 debited at Amazon"}'

# Get balance
curl http://localhost:5000/api/balance/current

# Get statistics
curl http://localhost:5000/api/balance/statistics
```

---

## 🌐 Deployment

### Heroku

```bash
git push heroku main
heroku config:set OPENAI_API_KEY=sk-...
heroku run python3 -c "from app import app; ..."
```

### AWS EC2

```bash
# Install dependencies
sudo apt-get install python3-pip python3-venv
pip install -r requirements.txt

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Environment Variables (Production)

```
FLASK_ENV=production
FLASK_APP=app.py
SECRET_KEY=<generate-secure-key>
OPENAI_API_KEY=<your-key>
DATABASE_URL=postgresql://...
PORT=5000
```

---

## 🐛 Troubleshooting

### "LLM API not responding"
- Check `OPENAI_API_KEY` in `.env`
- Verify API key is active
- Check rate limits
- Increase timeout from 10s to 30s in `llm_service.py`

### "Message already processed"
- This is intentional duplicate prevention
- Different message = new transaction
- Delete original if wrong entry

### "Balance not updating"
- Clear browser cache
- Refresh page
- Check database tables created
- Verify `UserBalance` table exists

### "Charts not displaying"
- Check Chart.js CDN is loaded
- Verify data format is correct
- Open browser console for errors

---

## 📚 Documentation

- **[TRANSACTION_PARSER_GUIDE.md](TRANSACTION_PARSER_GUIDE.md)** - Detailed feature documentation
- **[INTERVIEW_GUIDE.md](INTERVIEW_GUIDE.md)** - Interview Q&A
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
- **[README.md](README.md)** - Complete documentation
- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute setup

---

## 🎓 Learning Resources

### Understanding the Code
- Read `models/models.py` for database structure
- Study `services/llm_service.py` for AI integration
- Check `services/transaction_service.py` for message parsing logic
- Review `routes/transactions.py` for API design

### Extending Features
- Add recurring transactions
- Implement budget limits
- Create expense forecasts
- Add bill reminders
- Build mobile app with same API

---

## 📝 License

MIT License - Free to use and modify

---

## 🎉 Summary

This is a **complete, production-ready expense tracker** with:
- ✅ Automatic transaction detection from messages
- ✅ Smart AI categorization
- ✅ Real-time balance updates
- ✅ Comprehensive analytics
- ✅ Beautiful, responsive UI
- ✅ Security best practices
- ✅ Complete documentation

**Perfect for:**
- Personal finance management
- Resume/portfolio projects
- Technical interview preparation
- Learning Flask + AI integration
- Real-world deployment

---

**Version:** 2.0.0  
**Status:** Production-Ready  
**Last Updated:** January 3, 2024

---

### 🚀 Next Steps

1. Set up `.env` file with OpenAI API key
2. Run `python3 app.py`
3. Navigate to Messages section
4. Paste a transaction message
5. Watch the AI do the work!

**Enjoy effortless expense tracking!** 💰🤖
