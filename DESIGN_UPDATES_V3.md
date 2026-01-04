# AI-Powered Expense Tracker v3.0 - Design Updates

**Document Status:** Design Proposal (No code changes yet)  
**Target Version:** 3.0.0  
**Date:** January 3, 2026  
**Author:** Senior Product Engineer

---

## Executive Summary

This document proposes **5 major feature additions** to enhance the Expense Tracker with multi-currency support, income/savings separation, intelligent savings tracking, and advanced financial insights. All updates preserve existing functionality while introducing sophisticated financial tracking capabilities.

---

## 1. CURRENCY SELECTION & CHANGE

### Overview
Allow users to select and switch between currencies (INR, USD, EUR, GBP, JPY, etc.) while preserving original transaction amounts for accuracy.

### Database Schema Additions

**New Fields in `User` Model:**
```python
# In models/models.py → User class
preferred_currency = db.Column(db.String(3), default='INR', nullable=False)  # ISO 4217 code
currency_changed_at = db.Column(db.DateTime, nullable=True)
```

**New Table: `CurrencyHistory` (for audit trail)**
```python
class CurrencyHistory(db.Model):
    """Track all currency changes by user for audit and analytics"""
    __tablename__ = 'currency_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    old_currency = db.Column(db.String(3), nullable=False)
    new_currency = db.Column(db.String(3), nullable=False)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    reason = db.Column(db.String(255), nullable=True)  # e.g., "User relocation", "Manual change"
```

**Enhancement to `Income` & `Expense` Models:**
```python
# Add to both models
original_currency = db.Column(db.String(3), nullable=True)  # Currency at time of transaction
original_amount = db.Column(db.Float, nullable=True)  # Amount in original currency
```

**Enhancement to `Transaction` Model:**
```python
original_currency = db.Column(db.String(3), nullable=True)
original_amount = db.Column(db.Float, nullable=True)
```

### Feature Logic

#### 1.1 Currency Selection on Signup/Settings
- **UI Component**: Currency dropdown on registration & settings page
- **Supported Currencies**: INR, USD, EUR, GBP, JPY, AUD, CAD, CHF, CNY, SEK
- **Default**: INR (can be configured)
- **Update Mechanism**: 
  - User can change via settings page
  - Change recorded in `CurrencyHistory` table
  - System logs timestamp and reason (optional)

#### 1.2 Amount Storage Strategy
```
For each transaction (Income/Expense/Transaction):
1. Store amount in display currency (e.g., 500 USD)
2. Also store original_currency & original_amount for audit
3. On currency change:
   - Do NOT retroactively convert historical data
   - Display with conversion note: "₹41,500 (~500 USD at historical rate)"
   - Maintain data integrity with original amounts
```

#### 1.3 Display & Conversion Handling
```python
# New utility function in utils/currency.py
def get_display_amount(transaction, target_currency):
    """
    Returns amount for display in target currency
    If transaction was in different currency, show both
    """
    if transaction.original_currency == target_currency:
        return transaction.amount
    else:
        # Display with historical note
        return {
            'display_amount': transaction.amount,
            'original_currency': transaction.original_currency,
            'original_amount': transaction.original_amount,
            'note': 'Amount shown in current selected currency'
        }

# Real-time conversion (uses external API for current rates)
def convert_currency(amount, from_currency, to_currency):
    """
    Convert amount from one currency to another
    Uses cached rates (refresh every 6 hours)
    Falls back to historical rate if real-time unavailable
    """
    pass
```

#### 1.4 API Endpoints for Currency

**POST `/api/user/currency`**
```json
Request: {
  "new_currency": "USD",
  "reason": "Moved to US"  // optional
}
Response: {
  "success": true,
  "old_currency": "INR",
  "new_currency": "USD",
  "changed_at": "2026-01-03T10:30:00Z"
}
```

**GET `/api/currency/rates`**
```json
Response: {
  "success": true,
  "base_currency": "INR",
  "rates": {
    "USD": 0.012,
    "EUR": 0.011,
    "GBP": 0.0095,
    ...
  },
  "last_updated": "2026-01-03T10:00:00Z"
}
```

**GET `/api/user/currency/history`**
```json
Response: {
  "success": true,
  "current_currency": "USD",
  "history": [
    {
      "old_currency": "INR",
      "new_currency": "USD",
      "changed_at": "2026-01-03T10:30:00Z",
      "reason": "Moved to US"
    }
  ]
}
```

### UI/UX Changes
- **Settings Page**: Add currency selector with flag icons and current rate display
- **Dashboard Header**: Show current currency symbol next to balance
- **Transaction Lists**: Display amounts with currency symbol (₹, $, €, £, ¥)
- **Summary Page**: Add "Display in different currency" option for reports

---

## 2. ORIGINAL INCOME & SAVINGS SEPARATION

### Overview
Distinguish between three income streams:
- **Original Income**: Fixed salary or primary income
- **Added Money**: Manual credits, bonuses, top-ups
- **Actual Savings**: Unspent amount (calculated as: Original Income + Added Money - Expenses)

### Database Schema Additions

**New Fields in `UserBalance` Model:**
```python
# In models/models.py → UserBalance class
original_income = db.Column(db.Float, default=0.0)  # Fixed/primary income
added_money = db.Column(db.Float, default=0.0)  # Manual credits, bonuses, top-ups
actual_savings = db.Column(db.Float, default=0.0)  # calculated: original + added - spent
```

**New Table: `IncomeType` (classification)**
```python
class IncomeType(db.Model):
    """Categorize income sources for separation logic"""
    __tablename__ = 'income_types'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    income_id = db.Column(db.Integer, db.ForeignKey('incomes.id'), nullable=False)
    income_category = db.Column(
        db.String(20), 
        nullable=False
        # Values: 'original', 'bonus', 'refund', 'manual_credit', 'other'
    )
    monthly_recurring = db.Column(db.Boolean, default=False)  # e.g., salary is recurring
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('income_id', name='_income_once_'),)
```

**Enhancement to `Income` Model:**
```python
# In models/models.py → Income class
income_type = db.Column(
    db.String(20), 
    default='other',
    # Values: 'salary', 'bonus', 'refund', 'manual_credit', 'freelance', 'investment', 'other'
)
is_monthly_recurring = db.Column(db.Boolean, default=False)
```

### Feature Logic

#### 2.1 Income Classification
When a user adds income:
1. **Salary/Primary Income**: Auto-tagged as "original" if monthly recurring
2. **Other Credits**: Auto-tagged as "added_money"
3. **UI Prompt**: "Is this recurring income?" → Updates `is_monthly_recurring` flag

#### 2.2 Savings Calculation
```python
# Pseudo-code logic
def calculate_savings(user_id, month, year):
    """
    Calculate actual savings = Original Income + Added Money - Total Expenses
    Original Income never decreases with expenses
    """
    original_income = sum of all recurring monthly income for this month
    added_money = sum of non-recurring income for this month
    total_expenses = sum of all expenses for this month
    
    actual_savings = original_income + added_money - total_expenses
    
    return {
        'original_income': original_income,
        'added_money': added_money,
        'total_expenses': total_expenses,
        'actual_savings': actual_savings,
        'savings_rate': (actual_savings / (original_income + added_money)) * 100  # percentage
    }
```

#### 2.3 Original Income Protection
- **Rule**: Original income is NEVER overwritten by expenses
- **Implementation**: 
  - Store separately in `UserBalance.original_income`
  - Always calculate as: `Actual Balance = Original + Added - Spent`
  - If balance goes negative, it means "savings used" (tracked in separate field)

#### 2.4 API Endpoints

**POST `/api/income`** (Enhanced)
```json
Request: {
  "amount": 50000,
  "source": "Salary",
  "income_type": "salary",  // new field
  "is_monthly_recurring": true,  // new field
  "date": "2026-01-01"
}
Response: {
  "success": true,
  "income_id": 123,
  "income_type": "salary",
  "updated_balance": {
    "original_income": 50000,
    "added_money": 0,
    "actual_savings": 0,
    "total_expenses": 0
  }
}
```

**GET `/api/balance/breakdown`** (New)
```json
Response: {
  "success": true,
  "current_month": {
    "original_income": 50000,
    "added_money": 5000,
    "total_income": 55000,
    "total_expenses": 15000,
    "actual_savings": 40000,
    "savings_rate_percent": 72.7,
    "balance_status": "positive"  // positive, negative, zero
  },
  "previous_months": [
    {
      "month": "December",
      "year": 2025,
      "original_income": 50000,
      "added_money": 0,
      "actual_savings": 35000
    }
  ]
}
```

### UI/UX Changes
- **Dashboard Widget**: 
  ```
  ┌─────────────────────────────┐
  │ Income & Savings Breakdown  │
  ├─────────────────────────────┤
  │ Original Income:  ₹50,000   │
  │ + Added Money:    ₹5,000    │
  │ ─────────────────────────── │
  │ Total:            ₹55,000   │
  │ - Expenses:       ₹15,000   │
  │ ═════════════════════════════│
  │ Actual Savings:   ₹40,000   │
  │ Savings Rate:     72.7%     │
  └─────────────────────────────┘
  ```
- **Add Income Form**: New radio button options for income type
- **Balance History**: Show original income line in chart (never decreases)

---

## 3. SAVINGS TRACKING & CARRY FORWARD

### Overview
Track monthly savings explicitly and carry unused savings to the next month, with detailed monthly history.

### Database Schema Additions

**New Table: `MonthlySavings` (New)**
```python
class MonthlySavings(db.Model):
    """Track savings per month with carry-forward mechanism"""
    __tablename__ = 'monthly_savings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)  # 1-12
    
    # Opening balance
    opening_balance = db.Column(db.Float, default=0.0)  # Carried from previous month
    opening_from_month = db.Column(db.Integer, nullable=True)  # Which month carried from
    opening_from_year = db.Column(db.Integer, nullable=True)
    
    # Monthly transactions
    original_income = db.Column(db.Float, default=0.0)
    added_money = db.Column(db.Float, default=0.0)
    total_expenses = db.Column(db.Float, default=0.0)
    
    # Savings calculation
    monthly_savings = db.Column(db.Float, default=0.0)  # Income + Added - Expenses
    closing_balance = db.Column(db.Float, default=0.0)  # Opening + Monthly Savings
    
    # Carry-forward status
    carried_forward_to_month = db.Column(db.Integer, nullable=True)
    carried_forward_to_year = db.Column(db.Integer, nullable=True)
    carry_forward_amount = db.Column(db.Float, default=0.0)
    carried_forward_at = db.Column(db.DateTime, nullable=True)
    
    # Metadata
    currency = db.Column(db.String(3), default='INR')
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'year', 'month', name='_user_month_once_'),
    )
```

**New Table: `SavingsCarryForward` (Audit Trail)**
```python
class SavingsCarryForward(db.Model):
    """Track carry-forward operations for audit"""
    __tablename__ = 'savings_carry_forward'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    from_month = db.Column(db.Integer, nullable=False)
    from_year = db.Column(db.Integer, nullable=False)
    to_month = db.Column(db.Integer, nullable=False)
    to_year = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    automated = db.Column(db.Boolean, default=True)  # True if auto-carry, False if manual
    carried_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### Feature Logic

#### 3.1 Monthly Savings Calculation
```python
# Pseudo-code
def calculate_and_store_monthly_savings(user_id, month, year):
    """
    Calculate savings for a specific month and store in MonthlySavings
    Called at end of month or on-demand
    """
    
    # Get previous month's closing balance
    previous_month = month - 1 if month > 1 else 12
    previous_year = year if month > 1 else year - 1
    
    prev_month_record = MonthlySavings.query.filter_by(
        user_id=user_id,
        year=previous_year,
        month=previous_month
    ).first()
    
    opening_balance = prev_month_record.closing_balance if prev_month_record else 0.0
    
    # Get current month data
    original_income = sum of recurring income for this month
    added_money = sum of non-recurring income for this month
    total_expenses = sum of expenses for this month
    
    monthly_savings = original_income + added_money - total_expenses
    closing_balance = opening_balance + monthly_savings
    
    # Store in database
    savings_record = MonthlySavings(
        user_id=user_id,
        year=year,
        month=month,
        opening_balance=opening_balance,
        opening_from_month=previous_month,
        opening_from_year=previous_year,
        original_income=original_income,
        added_money=added_money,
        total_expenses=total_expenses,
        monthly_savings=monthly_savings,
        closing_balance=closing_balance,
        currency=user.preferred_currency
    )
    db.session.add(savings_record)
    db.session.commit()
    
    return savings_record
```

#### 3.2 Automatic Carry Forward
```python
# Pseudo-code
def auto_carry_forward_savings(user_id, from_month, from_year, to_month, to_year):
    """
    Automatically carry unused savings to next month
    Triggered at end of month or via scheduled task
    """
    
    from_record = MonthlySavings.query.filter_by(
        user_id=user_id,
        year=from_year,
        month=from_month
    ).first()
    
    if not from_record:
        return False
    
    carry_amount = from_record.closing_balance
    
    # Get or create 'to_month' record
    to_record = MonthlySavings.query.filter_by(
        user_id=user_id,
        year=to_year,
        month=to_month
    ).first()
    
    if not to_record:
        to_record = MonthlySavings(
            user_id=user_id,
            year=to_year,
            month=to_month
        )
    
    # Update opening balance with carry-forward
    to_record.opening_balance = carry_amount
    to_record.opening_from_month = from_month
    to_record.opening_from_year = from_year
    
    # Mark source as carried forward
    from_record.carried_forward_to_month = to_month
    from_record.carried_forward_to_year = to_year
    from_record.carry_forward_amount = carry_amount
    from_record.carried_forward_at = datetime.utcnow()
    
    # Audit log
    audit_log = SavingsCarryForward(
        user_id=user_id,
        from_month=from_month,
        from_year=from_year,
        to_month=to_month,
        to_year=to_year,
        amount=carry_amount,
        automated=True
    )
    
    db.session.add(audit_log)
    db.session.add(to_record)
    db.session.add(from_record)
    db.session.commit()
    
    return True
```

#### 3.3 Savings History Retrieval
```python
# API endpoint logic
def get_savings_history(user_id, months=12):
    """
    Get savings history for last N months
    Shows opening balance, transactions, closing balance
    """
    records = MonthlySavings.query.filter_by(user_id=user_id)\
        .order_by(MonthlySavings.year.desc(), MonthlySavings.month.desc())\
        .limit(months)\
        .all()
    
    return [
        {
            'month': r.month,
            'year': r.year,
            'opening_balance': r.opening_balance,
            'original_income': r.original_income,
            'added_money': r.added_money,
            'total_expenses': r.total_expenses,
            'monthly_savings': r.monthly_savings,
            'closing_balance': r.closing_balance,
            'carried_from': {
                'month': r.opening_from_month,
                'year': r.opening_from_year
            } if r.opening_from_month else None,
            'carried_to': {
                'month': r.carried_forward_to_month,
                'year': r.carried_forward_to_year
            } if r.carried_forward_to_month else None
        }
        for r in records
    ]
```

#### 3.4 API Endpoints

**GET `/api/savings/monthly-history`** (New)
```json
Query Parameters:
  - months: 6-12 (optional, default 6)
  - year: 2026 (optional)

Response: {
  "success": true,
  "user_currency": "INR",
  "history": [
    {
      "month": 1,
      "year": 2026,
      "opening_balance": 35000,
      "original_income": 50000,
      "added_money": 0,
      "total_expenses": 10000,
      "monthly_savings": 40000,
      "closing_balance": 75000,
      "carried_from": null,  // first month of data
      "carried_to": { "month": 2, "year": 2026 }
    }
  ]
}
```

**POST `/api/savings/carry-forward`** (Manual trigger, optional)
```json
Request: {
  "from_month": 12,
  "from_year": 2025,
  "to_month": 1,
  "to_year": 2026,
  "manual": true  // User-initiated
}

Response: {
  "success": true,
  "amount_carried": 75000,
  "to_opening_balance": 75000
}
```

**GET `/api/savings/current`** (New)
```json
Response: {
  "success": true,
  "current_month": {
    "month": 1,
    "year": 2026,
    "opening_balance": 35000,
    "total_so_far": 40000,  // Projected by summing current month's data
    "status": "on_track"  // on_track, exceeding, below
  }
}
```

### UI/UX Changes
- **Savings Dashboard**: 
  ```
  ┌──────────────────────────────┐
  │ Savings Tracker (Jan 2026)   │
  ├──────────────────────────────┤
  │ Opening Balance:  ₹35,000    │
  │ Monthly Savings:  ₹40,000    │
  │ ──────────────────────────── │
  │ Projected Close:  ₹75,000    │
  │                              │
  │ [Carry to Feb ▶] [View All]  │
  └──────────────────────────────┘
  ```
- **Savings History Chart**: Line chart showing opening → monthly savings → closing balance
- **Carry Forward Widget**: Manual button + automatic indicator

---

## 4. AUTOMATIC + MANUAL MONEY ADDITION

### Overview
Support credit transactions from message parsing (automatic) and manual cash/wallet top-ups, with clear tagging and balance impact.

### Database Schema Additions

**Enhancement to `Transaction` Model:**
```python
# In models/models.py → Transaction class
# (Already has transaction_type='Credit' or 'Debit')

# Add these fields for tagging
money_addition_type = db.Column(
    db.String(20),
    nullable=True
    # Values: 'auto_parsed', 'manual_credit', 'refund', 'bonus', 'bank_transfer'
)
is_verified = db.Column(db.Boolean, default=False)  # User confirms before balance update
verification_status = db.Column(
    db.String(20),
    default='pending'
    # Values: 'pending', 'verified', 'rejected'
)
verification_notes = db.Column(db.Text, nullable=True)  # User's notes on verification
verified_at = db.Column(db.DateTime, nullable=True)
```

**Enhancement to `Expense` Model:**
```python
# Also support manual credit via Expense model (for consistency)
is_credit_transaction = db.Column(db.Boolean, default=False)
credit_source = db.Column(db.String(100), nullable=True)  # e.g., "Refund", "Cashback"
```

### Feature Logic

#### 4.1 Automatic Money Addition Flow
```
User sends message: "Received ₹5000 bonus"
         ↓
LLM Parser detects CREDIT transaction
         ↓
System creates Transaction record with:
  - transaction_type = 'Credit'
  - money_addition_type = 'auto_parsed'
  - verification_status = 'pending'
  - is_verified = False
         ↓
Dashboard shows: "[Unverified] Bonus: ₹5000"
         ↓
User reviews and clicks "Verify" or "Reject"
         ↓
If Verified:
  - Update UserBalance (added_money += 5000)
  - Update MonthlySavings (added_money += 5000)
  - Set verification_status = 'verified'
  
If Rejected:
  - Keep record for audit
  - Do NOT update balance
  - Set verification_status = 'rejected'
```

#### 4.2 Manual Money Addition Flow
```
User clicks "Add Money" button
         ↓
Form: Amount | Source (Salary, Bonus, Manual Credit, etc.) | Date
         ↓
System creates Transaction record with:
  - transaction_type = 'Credit'
  - money_addition_type = 'manual_credit'
  - is_verified = True (user explicitly added)
         ↓
Immediately update UserBalance & MonthlySavings
         ↓
Show confirmation with new balance
```

#### 4.3 Verification UI Component
```python
# Pseudo-code for verification endpoint

def verify_auto_transaction(user_id, transaction_id, action='verify'):
    """
    Verify or reject an auto-parsed credit transaction
    action: 'verify' or 'reject'
    """
    transaction = Transaction.query.filter_by(
        id=transaction_id,
        user_id=user_id
    ).first()
    
    if not transaction:
        return {'success': False, 'message': 'Transaction not found'}
    
    if action == 'verify':
        # Update balance only on verification
        balance = UserBalance.query.filter_by(user_id=user_id).first()
        balance.added_money += transaction.amount
        balance.current_balance += transaction.amount
        
        transaction.is_verified = True
        transaction.verification_status = 'verified'
        transaction.verified_at = datetime.utcnow()
        
        # Update MonthlySavings if exists
        month_savings = MonthlySavings.query.filter_by(
            user_id=user_id,
            year=transaction.created_at.year,
            month=transaction.created_at.month
        ).first()
        if month_savings:
            month_savings.added_money += transaction.amount
            month_savings.closing_balance += transaction.amount
        
        db.session.commit()
        return {'success': True, 'message': 'Transaction verified and balance updated'}
    
    elif action == 'reject':
        transaction.verification_status = 'rejected'
        db.session.commit()
        return {'success': True, 'message': 'Transaction rejected'}
```

#### 4.4 API Endpoints

**POST `/api/money/add-manual`** (New)
```json
Request: {
  "amount": 5000,
  "source": "Bonus",  // Salary, Bonus, Refund, Manual Credit, Bank Transfer
  "description": "Performance bonus",
  "date": "2026-01-03"
}

Response: {
  "success": true,
  "transaction_id": 456,
  "added_money_type": "manual_credit",
  "updated_balance": {
    "added_money": 5000,
    "current_balance": 45000
  }
}
```

**PUT `/api/transactions/{id}/verify`** (New)
```json
Request: {
  "action": "verify",  // or "reject"
  "notes": "Confirmed received via bank"  // optional
}

Response: {
  "success": true,
  "verification_status": "verified",
  "updated_balance": {
    "added_money": 10000,
    "current_balance": 50000
  }
}
```

**GET `/api/transactions/pending-verification`** (New)
```json
Response: {
  "success": true,
  "pending_count": 3,
  "transactions": [
    {
      "id": 123,
      "type": "auto_parsed",
      "amount": 5000,
      "source": "Bonus",
      "parsed_from": "Received ₹5000 bonus",
      "created_at": "2026-01-03T10:00:00Z",
      "status": "pending"
    }
  ]
}
```

### UI/UX Changes
- **Dashboard - Unverified Credits Section**:
  ```
  ┌──────────────────────────────┐
  │ Pending Verification (3)     │
  ├──────────────────────────────┤
  │ [Auto] Bonus: ₹5000          │
  │ Parsed from: "Received..."   │
  │ [Verify] [Reject]            │
  │                              │
  │ [Manual] Top-up: ₹2000       │
  │ [Verify] [Reject]            │
  └──────────────────────────────┘
  ```
- **Add Money Button**: Quick access to manual credit addition form
- **Transaction List**: Badge showing "[Auto]" or "[Manual]" for each credit

---

## 5. AI-BASED SAVINGS INSIGHTS (UPDATE)

### Overview
Update LLM insights to focus on savings growth, original income usage, and impact of added money on spending habits. Adapt all insights to user's selected currency.

### Enhanced Insights Focus Areas

#### 5.1 Savings-Focused Metrics to Analyze
1. **Original Income Usage**
   - Percentage of original income spent
   - Trend: increasing/decreasing spending ratio
   - Anomalies: unusual spending patterns

2. **Savings Growth/Decline**
   - Month-over-month savings comparison
   - Savings rate trend (is user saving more?)
   - Projection: estimated savings in 6 months

3. **Impact of Added Money**
   - Does added money increase expenses?
   - Comparison: spending with/without added money
   - Insight: "You tend to spend 30% more when you have bonus money"

4. **Category Analysis**
   - Which categories consume original income?
   - Which categories benefit from added money?
   - Budgeting recommendations

5. **Savings Behavior**
   - Consistency: regular savers vs. irregular
   - Stability: savings variance
   - Goal tracking: "On track to save ₹500,000 by Dec 2026"

### Updated Prompts for LLM

**Prompt 1: Savings-Focused Monthly Insights**
```
User provided data:
- Currency: {user_currency}
- Current Month: {month} {year}
- Opening Balance: {opening_balance} {currency}
- Original Income: {original_income} {currency}
- Added Money: {added_money} {currency}
- Total Expenses: {total_expenses} {currency}
- Monthly Savings: {monthly_savings} {currency}
- Savings Rate: {savings_rate}%

Previous 3 Months Data:
{previous_months_data}

Expense Breakdown:
{expense_by_category}

Task: Generate 3-4 paragraphs of actionable insights focusing on:
1. Savings growth trend and sustainability
2. How effectively original income is being used
3. Impact of added money on spending patterns
4. Specific recommendations to improve savings rate

Requirements:
- Use the exact currency symbol {currency}
- Be specific with numbers and percentages
- Provide at least 1 actionable recommendation
- Tone: Encouraging but realistic
- Language: Simple, non-technical

Output ONLY the insights text, no JSON.
```

**Prompt 2: Savings Goal & Projection**
```
Current Monthly Savings: {monthly_savings} {currency}
Average Monthly Savings (last 6 months): {avg_savings} {currency}
User's Projected Savings (next 6 months): {projected_savings} {currency}

Generate a brief projection statement (2-3 sentences) for the user:
- "At your current savings rate of {rate}, you will save approximately {amount} by {date}"
- Include confidence level: High/Medium/Low
- Suggest whether to increase savings or if on good track

Use currency: {currency}
```

**Prompt 3: Anomaly Detection**
```
Compare current month to average of last 6 months:

Current Month:
- Expenses: {current_expenses} {currency}
- Added Money: {current_added_money} {currency}

Last 6 Months Average:
- Expenses: {avg_expenses} {currency}
- Added Money: {avg_added_money} {currency}

If any value deviates by >25%, generate a brief insight:
- "Your expenses are 40% higher than normal. Check {highest_category}."
- Or: "Great! You received bonus money but kept expenses stable."

Be factual and actionable.
```

### Enhanced LLM Service

**New Method: `generate_savings_insights`**
```python
def generate_savings_insights(
    self,
    user_currency: str,
    financial_data: Dict,
    previous_months: List[Dict],
    expense_breakdown: Dict
) -> Optional[str]:
    """
    Generate savings-focused insights
    
    Args:
        user_currency: 'INR', 'USD', etc.
        financial_data: {
            'month': 'January',
            'year': 2026,
            'opening_balance': 35000,
            'original_income': 50000,
            'added_money': 0,
            'total_expenses': 10000,
            'monthly_savings': 40000,
            'savings_rate': 80.0
        }
        previous_months: List of 3-6 months data
        expense_breakdown: {
            'Food': 3000,
            'Travel': 2000,
            ...
        }
    
    Returns:
        str: AI-generated insights text
    """
    # Implementation calls _make_api_call with savings-focused prompt
```

**New Method: `generate_savings_projection`**
```python
def generate_savings_projection(
    self,
    user_currency: str,
    current_monthly_savings: float,
    avg_monthly_savings: float,
    last_n_months: int = 6
) -> Optional[Dict]:
    """
    Generate savings projection for next 6 months
    
    Returns:
        {
            'projection': "At current rate, you'll save ₹240,000 by June 2026",
            'confidence': 'High',
            'recommendation': 'On track. Consider increasing savings target.',
            'projected_total': 240000
        }
    """
    pass
```

**New Method: `detect_spending_anomalies`**
```python
def detect_spending_anomalies(
    self,
    user_currency: str,
    current_expenses: float,
    avg_expenses: float,
    current_added_money: float,
    avg_added_money: float,
    expense_breakdown: Dict
) -> Optional[str]:
    """
    Detect anomalies in spending or added money patterns
    
    Returns insight string if anomalies detected, else None
    """
    pass
```

### Enhanced API Response

**GET `/api/summary/ai-insights`** (Updated)
```json
Response: {
  "success": true,
  "month": "January",
  "year": 2026,
  "currency": "INR",
  "summary": {
    "opening_balance": 35000,
    "original_income": 50000,
    "added_money": 0,
    "total_expenses": 10000,
    "monthly_savings": 40000,
    "savings_rate": 80.0
  },
  "insights": {
    "savings_analysis": "Your savings of ₹40,000 this month is excellent... [3-4 paragraphs]",
    "projection": {
      "statement": "At current rate, you'll save ₹240,000 by June 2026",
      "confidence": "High",
      "recommendation": "On track. Consider increasing target.",
      "projected_total": 240000
    },
    "anomalies": "Your food spending (₹3,000) is 20% higher than usual... [if any]",
    "category_breakdown": {
      "Food": {"amount": 3000, "vs_average": "+20%", "insight": "Higher than usual"},
      "Travel": {"amount": 2000, "vs_average": "-10%"}
    }
  }
}
```

### Currency Adaptation
```python
# New utility in services/llm_service.py

def adapt_insights_to_currency(
    self,
    insights_text: str,
    from_currency: str,
    to_currency: str,
    financial_data: Dict
) -> str:
    """
    Adapt existing insights to different currency
    
    If user changes currency mid-month:
    1. Keep original amounts in original currency
    2. Show conversion: "₹40,000 (~USD 480 at current rate)"
    3. Regenerate insights if needed for accuracy
    """
    pass
```

### UI/UX Changes
- **Insights Widget**: 
  ```
  ┌──────────────────────────────┐
  │ AI Savings Insights          │
  ├──────────────────────────────┤
  │ 📊 Savings Analysis           │
  │ Your savings of ₹40,000 this  │
  │ month is excellent...         │
  │ [Read More]                  │
  │                              │
  │ 📈 6-Month Projection         │
  │ ₹240,000 by June 2026 (High)  │
  │                              │
  │ ⚠️ Anomaly Detected           │
  │ Food spending 20% higher      │
  └──────────────────────────────┘
  ```
- **Insights Page**: Full insights with charts and recommendations
- **Category Insights**: Hover over chart bars to see "vs. average" comparison

---

## Data Flow Diagram

```
User Authentication
    ↓
[Dashboard Load]
    ↓
├─→ Fetch UserBalance (original_income, added_money, actual_savings)
├─→ Fetch MonthlySavings (opening, transactions, closing)
├─→ Fetch Currency (preferred_currency, display all amounts)
├─→ Fetch PendingVerification (auto-parsed credits awaiting confirmation)
└─→ Display:
    - Savings Tracking Widget
    - Income & Expenses Breakdown
    - Pending Verifications
    - AI Savings Insights
    
[User adds transaction]
    ↓
    ├─→ Debit (Expense)
    │   └─→ Update UserBalance.total_debits & current_balance
    │   └─→ Update MonthlySavings.total_expenses & closing_balance
    │   └─→ Regenerate AI Insights (if category spend anomaly)
    │
    └─→ Credit (Manual)
        └─→ Immediately update balance
        └─→ Mark as verified
        
[User receives message]
    ↓
    ├─→ LLM Parse (transaction_type, amount, source, category)
    ├─→ Create Transaction (verification_status = 'pending')
    ├─→ Show in "Pending Verification" list
    └─→ User clicks Verify
        └─→ Update UserBalance.added_money & current_balance
        └─→ Update MonthlySavings
        └─→ Set Transaction.is_verified = True
        
[Month Ends]
    ↓
    ├─→ Calculate MonthlySavings record (if not exists)
    ├─→ Auto Carry Forward to next month
    ├─→ Generate "Monthly Summary" email/notification
    └─→ Regenerate YoY and trailing projections
    
[User Changes Currency]
    ↓
    ├─→ Update User.preferred_currency
    ├─→ Log in CurrencyHistory
    ├─→ Display all amounts with new currency symbol
    ├─→ Optionally regenerate insights with conversion notes
    └─→ Keep original_currency & original_amount in DB
```

---

## Database Schema Summary

### New Tables
1. **CurrencyHistory** - Track currency changes
2. **MonthlySavings** - Explicit monthly savings records
3. **SavingsCarryForward** - Audit trail for carry-forward
4. **IncomeType** (optional) - Further income categorization

### Enhanced Fields

| Table | Field | Type | Purpose |
|-------|-------|------|---------|
| User | preferred_currency | String(3) | Currency code (INR, USD, etc.) |
| User | currency_changed_at | DateTime | Last currency change timestamp |
| Income | income_type | String(20) | salary, bonus, freelance, other |
| Income | is_monthly_recurring | Boolean | Mark recurring income |
| Expense | original_currency | String(3) | Currency at transaction time |
| Expense | original_amount | Float | Amount in original currency |
| Transaction | original_currency | String(3) | Original transaction currency |
| Transaction | original_amount | Float | Original transaction amount |
| Transaction | money_addition_type | String(20) | auto_parsed, manual_credit, etc. |
| Transaction | is_verified | Boolean | User confirmed transaction |
| Transaction | verification_status | String(20) | pending, verified, rejected |
| UserBalance | original_income | Float | Fixed/primary income sum |
| UserBalance | added_money | Float | Bonuses/credits sum |
| UserBalance | actual_savings | Float | Calculated savings amount |

---

## API Endpoints Summary

### New Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/user/currency` | Change preferred currency |
| GET | `/api/currency/rates` | Get current currency exchange rates |
| GET | `/api/user/currency/history` | View currency change history |
| GET | `/api/balance/breakdown` | Get original income + added money breakdown |
| GET | `/api/savings/monthly-history` | View savings for last N months |
| GET | `/api/savings/current` | Get current month savings projection |
| POST | `/api/savings/carry-forward` | Manually trigger carry-forward |
| POST | `/api/money/add-manual` | Add money manually (not from message) |
| PUT | `/api/transactions/{id}/verify` | Verify/reject auto-parsed credit |
| GET | `/api/transactions/pending-verification` | Get all pending verifications |
| GET | `/api/summary/ai-insights` | Get updated savings-focused insights |

### Modified Endpoints
| Endpoint | Changes |
|----------|---------|
| POST `/api/income` | Add `income_type`, `is_monthly_recurring` fields |
| GET `/api/summary/monthly` | Add `original_income`, `added_money`, `actual_savings` |
| GET `/api/summary/ai-insights` | Add savings projection, anomaly detection, currency |

---

## Interview-Ready Explanation

### Business Context
"We're enhancing the Expense Tracker to provide users with sophisticated financial insights focused on **sustainable savings growth** rather than just expense tracking. The key innovation is separating income types and automatically tracking savings with month-to-month carry-forward, enabling users to understand their actual financial position."

### Technical Approach
1. **Data Model**: Extended models to track income type, savings state, and transaction verification
2. **Separation of Concerns**: Created dedicated `MonthlySavings` table for explicit monthly tracking (not just calculated)
3. **Verification Flow**: Auto-parsed credits from LLM are marked "pending" until user confirms, ensuring data accuracy
4. **Carry-Forward Logic**: Month-end automated savings carry-forward with audit trail for compliance
5. **LLM Enhancement**: Shifted from generic insights to savings-focused analysis with anomaly detection

### Key Design Decisions
- **Why separate original_income from added_money?**
  - "Original income is the user's primary cash flow; added money is irregular. Separating them helps users understand true financial stability."
  
- **Why verification step for auto-parsed credits?**
  - "LLM parsing can have ~90% accuracy. Verification ensures users control balance updates and catch misclassifications."
  
- **Why store original_currency in every transaction?**
  - "If user changes currency, we preserve data integrity. Conversion is display-layer, not data-layer."
  
- **Why explicit MonthlySavings table instead of calculated?**
  - "Explicit records enable fast queries, historical analysis, and carry-forward logic without re-calculating. Improves performance."

### Scalability Considerations
- Currency rates: Cached with 6-hour TTL to avoid rate-limit hits
- Verification queue: Indexed on `verification_status` for fast pending query
- MonthlySavings: Unique constraint on (user_id, year, month) ensures one record per month
- Insights generation: Can be cached/scheduled task instead of on-demand

---

## Implementation Priority

### Phase 1 (Foundation)
1. Add currency selection to User model
2. Add income_type to Income model
3. Create MonthlySavings table
4. Implement carry-forward logic

### Phase 2 (Verification)
1. Add verification fields to Transaction model
2. Create verification API endpoints
3. Build verification UI widget

### Phase 3 (Insights)
1. Create new LLM prompts
2. Implement savings-focused insight generation
3. Add projection and anomaly detection

### Phase 4 (Polish)
1. Currency conversion utility
2. Exchange rate caching
3. UI refinements and testing

---

## Success Metrics

1. **User Engagement**
   - % of users setting up original income
   - % of users using carry-forward
   - % of users with verified auto-parsed credits

2. **Data Quality**
   - Accuracy of auto-parsed transactions (track vs. manual)
   - Verification rate (% of auto credits verified vs. rejected)

3. **Product Adoption**
   - Monthly active users viewing savings insights
   - Click-through rate on carry-forward button
   - Time spent on insights page

---

## Document End

This design is complete and ready for implementation. All 5 features are proposed, with detailed data models, API contracts, logic flows, and UI/UX guidance. No code has been modified; this is purely a design proposal.

