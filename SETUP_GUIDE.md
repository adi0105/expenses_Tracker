# 💰 Expense Tracker - Final Setup & Running Guide

## ✅ Current Status
The app is **fully working** with the following features:
- ✓ User registration & login with secure session management
- ✓ Dashboard with Overview, Transactions, Expenses, Income, Analytics sections  
- ✓ AI-powered transaction message processing (auto-detect expenses from SMS/alerts)
- ✓ Currency settings with custom symbol support
- ✓ Balance tracking and transaction statistics
- ✓ Accessibility features (ARIA labels, live regions, skip links, keyboard navigation)
- ✓ Security headers (CSP, X-Frame-Options, HSTS in production)
- ✓ Responsive sidebar toggle with persistent state

---

## 🚀 Quick Start

### Prerequisites
```bash
python3 --version  # Ensure Python 3.11+
```

### Installation & Running
```bash
cd /Users/aditya/Desktop/yuvraj/myProjects/expence_tracker_withGenerative_AI/expenses_Tracker

# Install dependencies (if not already done)
pip3 install -q flask flask-sqlalchemy flask-cors python-dotenv requests

# Set environment variables and start the server
export OPENAI_API_KEY='sk-test-demo'
export FLASK_ENV=development
export SECRET_KEY='test-secret'
export PORT=8888

python3 app.py
```

Access the app at: **http://127.0.0.1:8888**

---

## 📋 Testing Workflow

### 1. **Register a New User**
- Go to http://127.0.0.1:8888/api/auth/login → "Register here" link
- Fill in: username, email, password, select currency (INR/USD/EUR)
- Click Register

### 2. **Log In**
- Use credentials from registration
- You'll be redirected to the Dashboard

### 3. **Add Income**
- Click "Income" in sidebar
- Click "+ Add Income"
- Fill: Amount, Source (e.g., "Salary"), Date
- Click "Add Income"
- Verify in dashboard "Total Income" card updates

### 4. **Add Expenses**
- Click "Expenses" in sidebar
- Click "+ Add Expense"
- Fill: Amount, Description, Category, Date
- Click "Add Expense"
- Verify balance and expense breakdown update

### 5. **Process Transaction Message** (AI-powered)
- Click "Messages" in sidebar
- Paste a transaction alert: e.g., "₹2,500 debited from your account via UPI at Amazon"
- Click "Process Message"
- System auto-detects category and amount

### 6. **Change Currency**
- Click Settings (⚙️ top-right)
- Change currency dropdown (INR → USD, EUR, etc.)
- Optionally set custom symbol (e.g., "$")
- Click "Save Currency"
- Return to dashboard → all amounts now display in new currency

### 7. **Verify Accessibility**
- Press `Tab` to navigate sections
- Check screen reader announcements (notifications have `aria-live="polite"`)
- Click ☰ (hamburger) to toggle sidebar responsiveness

---

## 📁 Project Structure
```
expenses_Tracker/
├── app.py                          # Main Flask app (app factory)
├── config.py                       # Configuration (dev/prod/test)
├── models/
│   └── models.py                   # SQLAlchemy ORM models (User, Expense, Income, etc)
├── routes/
│   ├── auth.py                     # Registration, login, logout
│   ├── expenses.py                 # Expense CRUD
│   ├── income.py                   # Income CRUD
│   ├── transactions.py             # AI message processing, balance, stats (lazy-loaded)
│   ├── summary.py                  # Monthly summaries & reports
│   └── settings.py                 # Currency & profile settings
├── services/
│   ├── llm_service.py              # OpenAI integration (lazy init)
│   ├── transaction_service.py      # Transaction processing (lazy init)
│   └── ...other services
├── templates/
│   ├── dashboard.html              # Main dashboard UI (data-amount spans for currency)
│   ├── settings.html               # Settings/currency page
│   ├── auth/
│   │   ├── login.html              # Login form
│   │   └── register.html           # Registration form
│   └── errors/
├── static/
│   ├── css/style.css               # Global styles (skip-link, sidebar, focus outlines, etc)
│   ├── js/
│   │   ├── app.js                  # Core app logic (sidebar toggle, notifications, auth check)
│   │   ├── currency.js             # Client-side currency formatting (CurrencyManager)
│   │   ├── dashboard.js            # Load & render overview, expenses, income, charts
│   │   └── transactions.js         # AI message processing, balance updates
│   └── ...Chart.js library
├── utils/
│   ├── currency.py                 # Currency metadata & validation
│   ├── helpers.py                  # Email validation, decorators, auth helpers
│   └── ...
├── instance/
│   └── expense_tracker.db          # SQLite database (auto-created on first run)
└── requirements.txt                # Python dependencies (optional)
```

---

## 🔐 Security Features Implemented

### Session & Auth
- ✅ Secure session cookies (HTTPONLY, SAMESITE=Lax, SECURE in production)
- ✅ Password validation (min 6 chars, bcrypt hashing ready)
- ✅ Login required decorator on protected endpoints

### HTTP Security Headers
- ✅ **CSP** (Content-Security-Policy): Restricts script/style origins
- ✅ **X-Frame-Options**: DENY (prevents clickjacking)
- ✅ **X-Content-Type-Options**: nosniff (prevents MIME sniffing)
- ✅ **Referrer-Policy**: no-referrer-when-downgrade
- ✅ **Permissions-Policy**: Disables geolocation & microphone
- ✅ **HSTS**: Enforced in production (max-age=31536000)

### CORS
- ✅ CORS configured via `CORS_ALLOWED_ORIGINS` env var (defaults to same-origin only)
- ✅ Credentials included in same-origin requests

---

## 🎨 Accessibility (A11y) Improvements

- ✅ **Skip-to-main-content link** at top of page
- ✅ **ARIA labels & roles** on navigation, main, banner, status
- ✅ **Live regions** (aria-live="polite") for notifications & balance updates
- ✅ **Visible focus outlines** (4px solid blue on `:focus`)
- ✅ **Keyboard navigation**: Tab through fields, Sidebar toggle with Space/Enter
- ✅ **Screen reader announcements** for form submission, data loading
- ✅ **Semantic HTML**: Proper heading hierarchy, form labels

---

## 💾 Database Schema

### Key Tables
- **users**: id, username, email, password_hash, preferred_currency (INR|USD|EUR|etc), preferred_currency_symbol, created_at
- **expenses**: id, user_id, amount, description, category, date, ai_classified, created_at
- **incomes**: id, user_id, amount, source, date, created_at
- **transactions**: id, user_id, amount, type (Debit/Credit), merchant_or_source, category, date, is_auto_detected
- **expense_tracker.db**: SQLite file (auto-created in `instance/` folder)

---

## 🔄 API Endpoints Summary

### Auth
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Log in user
- `POST /api/auth/logout` - Log out
- `GET /api/auth/check-session` - Check if authenticated

### Expenses
- `GET /api/expenses/list` - List expenses
- `POST /api/expenses/add` - Add expense
- `DELETE /api/expenses/:id` - Delete expense

### Income
- `GET /api/incomes/list` - List incomes
- `POST /api/incomes/add` - Add income
- `DELETE /api/incomes/:id` - Delete income

### Transactions (AI-powered)
- `POST /api/transactions/upload-message` - Process SMS/alert message
- `GET /api/transactions/auto` - List auto-detected transactions
- `PUT /api/transactions/:id` - Edit transaction
- `DELETE /api/transactions/:id` - Delete transaction

### Balance & Stats
- `GET /api/balance/current` - Get current balance
- `GET /api/balance/statistics` - Get transaction stats

### Summary & Reports
- `GET /api/summary/monthly` - Get monthly income/expense/savings

### Settings
- `GET /api/settings/currency` - Get current currency preference
- `POST /api/settings/currency` - Update currency
- `GET /api/settings/currencies` - List all currencies
- `GET /api/settings/profile` - Get user profile

---

## 🐛 Troubleshooting

### App won't start
- Ensure `OPENAI_API_KEY` is set (even with dummy value like `'sk-test-demo'`)
- Check port isn't already in use: `lsof -iTCP:8888 -P`
- Kill any lingering processes: `pkill -9 python3`

### Database errors
- Delete `instance/expense_tracker.db` to reset
- App will auto-create tables on first run

### Currency not updating in dashboard
- Refresh browser (Cmd+Shift+R for hard refresh)
- Check browser console for JS errors
- Verify `/api/settings/currency` returns correct currency code

### Slow performance
- This is normal in development mode (debug=True)
- For production, use a WSGI server (gunicorn, uWSGI)

---

## 🚢 Deployment (Production)

### Environment Variables Required
```bash
OPENAI_API_KEY=sk-xxxx...          # Your OpenAI key
FLASK_ENV=production               # Set to production
SECRET_KEY=<generate-random-secret># Use a strong random key
PORT=8000                          # Optional (default 5000)
CORS_ALLOWED_ORIGINS=https://yourdomain.com  # Restrict CORS
DATABASE_URL=postgresql://...      # Use PostgreSQL in production (not SQLite)
```

### Run with Gunicorn (recommended)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Run with Docker (future)
Create a `Dockerfile` with Python base, install deps, expose port 8000

---

## 📝 Notes

1. **AI Features**: Requires valid OpenAI API key for transaction classification. Dummy key works for UI testing but AI endpoints will fail.
2. **Database**: Uses SQLite by default. For production, migrate to PostgreSQL.
3. **Currency Formatting**: Entirely client-side (browser does formatting). Custom symbols override server defaults.
4. **Performance**: Lazy-loading of LLM service prevents app startup hangs.

---

## ✨ You're all set!
The app is **fully functional** and **ready to use**. Enjoy tracking your expenses! 💸

