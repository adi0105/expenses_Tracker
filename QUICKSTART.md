# Expense Tracker - Quick Start Guide

Get the application running in 5 minutes!

## 🚀 Quick Start

### 1. **Prerequisites**
```bash
# Check Python version (3.8+)
python3 --version

# Check pip
pip3 --version
```

### 2. **Clone & Navigate**
```bash
cd expenses_Tracker
```

### 3. **Virtual Environment**
```bash
# Create
python3 -m venv venv

# Activate
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows
```

### 4. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 5. **Configure Environment**
```bash
# Copy example file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-...your-key...
```

### 6. **Initialize Database**
```python
python3
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

### 7. **Run Application**
```bash
python3 app.py
```

### 8. **Open in Browser**
```
http://localhost:5000
```

## 🧪 Test the Application

### Create Account
1. Click "Register here"
2. Enter: username, email, password
3. Click "Create Account"

### Login
1. Use credentials from registration
2. Click "Login"

### Add Expense
1. Click "Expenses" in sidebar
2. Click "+ Add Expense"
3. Enter amount and description
4. Click "🤖 Auto-Classify" (uses AI!)
5. Click "Add Expense"

### View Insights
1. Click "AI Insights" in sidebar
2. Click "🤖 Generate Insights"
3. See AI-powered financial advice

## ⚠️ Important Notes

1. **OpenAI API Key Required**
   - Get free key: https://platform.openai.com/api-keys
   - Add to `.env` file
   - You'll need credits for API calls

2. **Database**
   - Default: SQLite (expense_tracker.db)
   - Created automatically on first run

3. **Security**
   - Change `SECRET_KEY` in `.env` for production
   - Never commit `.env` file to git

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Change port in app.py
app.run(port=5001)
```

### Database Error
```bash
# Recreate database
rm expense_tracker.db
python3 app.py
```

### OpenAI API Error
- Check API key in `.env`
- Verify you have credits
- Check internet connection

## 📱 Features to Try

✅ Auto-classify expenses with AI  
✅ Generate monthly financial insights  
✅ View spending by category  
✅ Track income sources  
✅ See savings calculation  
✅ View yearly trends  

---

**Happy Tracking! 💰**
