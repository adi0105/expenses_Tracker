"""
Transaction Processing Service Module
Handles auto-detection, balance updates, and transaction management

This service implements:
1. Message parsing and auto-detection
2. Automatic balance updates (Credit/Debit)
3. Duplicate detection
4. Transaction management
"""

from typing import Optional, Dict, Tuple
from datetime import datetime, date
from models.models import (
    db, Expense, Transaction, UserBalance, User, Income
)
from services.llm_service import LLMService
import hashlib


class TransactionService:
    """
    Service for processing transactions from messages and managing auto-detection
    
    Features:
    - Parse transaction messages using LLM
    - Automatically update balance
    - Detect and prevent duplicates
    - Edit and delete transactions
    """
    
    def __init__(self):
        """Initialize transaction service with LLM service"""
        self.llm_service = LLMService()
    
    @staticmethod
    def generate_message_hash(message_text: str) -> str:
        """
        Generate SHA256 hash of message to detect duplicates
        
        Args:
            message_text: Original message text
        
        Returns:
            str: SHA256 hash in hexadecimal format
        """
        return hashlib.sha256(message_text.encode()).hexdigest()
    
    def check_duplicate_message(self, user_id: int, message_hash: str) -> bool:
        """
        Check if message has already been processed (duplicate detection)
        
        Args:
            user_id: User ID
            message_hash: Hash of message to check
        
        Returns:
            bool: True if duplicate exists, False otherwise
        """
        existing = Transaction.query.filter_by(
            user_id=user_id,
            message_hash=message_hash
        ).first()
        
        return existing is not None
    
    def process_transaction_message(
        self,
        user_id: int,
        message_text: str
    ) -> Tuple[bool, Optional[Dict], str]:
        """
        Process a transaction message (SMS/alert) end-to-end
        
        Steps:
        1. Check for duplicates
        2. Parse message with LLM
        3. Create transaction record
        4. Update user balance
        5. Create expense entry
        
        Args:
            user_id: User ID processing the message
            message_text: Raw transaction message text
        
        Returns:
            Tuple of (success: bool, transaction_data: Dict or None, message: str)
        
        Example:
            >>> service = TransactionService()
            >>> success, data, msg = service.process_transaction_message(
            ...     user_id=1,
            ...     message_text="₹2,500 debited from your account via UPI at Amazon"
            ... )
        """
        
        # Step 1: Generate hash and check for duplicates
        message_hash = self.generate_message_hash(message_text)
        
        if self.check_duplicate_message(user_id, message_hash):
            return False, None, "This message has already been processed. Skipping duplicate."
        
        # Step 2: Parse message with LLM
        parsed_data = self.llm_service.parse_transaction_message(message_text)
        
        if not parsed_data:
            # Save transaction with error status
            transaction = Transaction(
                user_id=user_id,
                message_text=message_text,
                message_hash=message_hash,
                processing_status='error',
                error_message='Failed to parse message with LLM'
            )
            db.session.add(transaction)
            db.session.commit()
            return False, None, "Failed to parse message. Try providing more details."
        
        try:
            # Step 3: Create transaction record
            transaction = Transaction(
                user_id=user_id,
                message_text=message_text,
                message_hash=message_hash,
                transaction_type=parsed_data['transaction_type'],
                amount=parsed_data['amount'],
                merchant_or_source=parsed_data['merchant_or_source'],
                category=parsed_data['expense_category'],
                processing_status='processed',
                raw_llm_response=str(parsed_data),
                processed_at=datetime.utcnow()
            )
            db.session.add(transaction)
            db.session.flush()
            
            # Step 4: Update user balance
            balance_updated = self.update_balance(
                user_id=user_id,
                amount=parsed_data['amount'],
                transaction_type=parsed_data['transaction_type']
            )
            
            if not balance_updated:
                db.session.rollback()
                return False, None, "Failed to update balance. Please try again."
            
            # Step 5: Create expense/income entry
            today = date.today()
            
            if parsed_data['transaction_type'] == 'Debit':
                # Create expense entry
                expense = Expense(
                    user_id=user_id,
                    amount=parsed_data['amount'],
                    description=f"Auto: {parsed_data['merchant_or_source']}",
                    category=parsed_data['expense_category'],
                    date=today,
                    ai_classified=True,
                    transaction_type='Debit',
                    merchant_or_source=parsed_data['merchant_or_source'],
                    is_auto_detected=True,
                    message_hash=message_hash,
                    original_message=message_text
                )
                db.session.add(expense)
            else:  # Credit
                # Create income entry
                income = Income(
                    user_id=user_id,
                    amount=parsed_data['amount'],
                    source=parsed_data['merchant_or_source'],
                    date=today
                )
                db.session.add(income)
            
            db.session.commit()
            
            return True, parsed_data, f"Transaction processed successfully! {parsed_data['transaction_type']} of ₹{parsed_data['amount']:.2f} from {parsed_data['merchant_or_source']}"
        
        except Exception as e:
            db.session.rollback()
            print(f"Transaction processing error: {e}")
            return False, None, f"Error processing transaction: {str(e)}"
    
    def update_balance(
        self,
        user_id: int,
        amount: float,
        transaction_type: str
    ) -> bool:
        """
        Update user balance based on transaction type
        
        Logic:
        - Debit: Subtract from current balance, add to total_debits
        - Credit: Add to current balance, add to total_credits
        
        Args:
            user_id: User ID
            amount: Transaction amount
            transaction_type: 'Debit' or 'Credit'
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get or create balance record
            balance = UserBalance.query.filter_by(user_id=user_id).first()
            
            if not balance:
                balance = UserBalance(user_id=user_id)
                db.session.add(balance)
                db.session.flush()
            
            # Update balance based on transaction type
            if transaction_type == 'Debit':
                balance.current_balance -= amount
                balance.total_debits += amount
            elif transaction_type == 'Credit':
                balance.current_balance += amount
                balance.total_credits += amount
            else:
                return False
            
            balance.last_updated = datetime.utcnow()
            db.session.commit()
            return True
        
        except Exception as e:
            print(f"Balance update error: {e}")
            return False
    
    def get_user_balance(self, user_id: int) -> Optional[Dict]:
        """
        Get current user balance
        
        Args:
            user_id: User ID
        
        Returns:
            Dict with balance info or None if not found
        """
        balance = UserBalance.query.filter_by(user_id=user_id).first()
        
        if balance:
            return balance.to_dict()
        
        return {
            'current_balance': 0.0,
            'total_credits': 0.0,
            'total_debits': 0.0
        }
    
    def edit_auto_transaction(
        self,
        expense_id: int,
        user_id: int,
        updates: Dict
    ) -> Tuple[bool, str]:
        """
        Edit an auto-detected transaction
        
        Updates the expense entry and adjusts balance accordingly
        
        Args:
            expense_id: Expense record ID
            user_id: User ID (for verification)
            updates: Dict with fields to update (amount, category, description, etc.)
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            expense = Expense.query.filter_by(
                id=expense_id,
                user_id=user_id,
                is_auto_detected=True
            ).first()
            
            if not expense:
                return False, "Auto-detected transaction not found."
            
            old_amount = expense.amount
            
            # Update fields if provided
            if 'amount' in updates:
                expense.amount = float(updates['amount'])
            if 'category' in updates:
                expense.category = updates['category']
            if 'description' in updates:
                expense.description = updates['description']
            if 'merchant_or_source' in updates:
                expense.merchant_or_source = updates['merchant_or_source']
            
            # Adjust balance if amount changed
            if 'amount' in updates and old_amount != expense.amount:
                difference = old_amount - expense.amount
                balance = UserBalance.query.filter_by(user_id=user_id).first()
                if balance:
                    balance.current_balance += difference  # Add back difference
                    balance.last_updated = datetime.utcnow()
            
            db.session.commit()
            return True, "Transaction updated successfully."
        
        except Exception as e:
            db.session.rollback()
            return False, f"Error updating transaction: {str(e)}"
    
    def delete_auto_transaction(
        self,
        expense_id: int,
        user_id: int
    ) -> Tuple[bool, str]:
        """
        Delete an auto-detected transaction
        
        Removes the expense entry and reverses the balance update
        
        Args:
            expense_id: Expense record ID
            user_id: User ID (for verification)
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            expense = Expense.query.filter_by(
                id=expense_id,
                user_id=user_id,
                is_auto_detected=True
            ).first()
            
            if not expense:
                return False, "Auto-detected transaction not found."
            
            amount = expense.amount
            
            # Reverse the balance update
            balance = UserBalance.query.filter_by(user_id=user_id).first()
            if balance:
                if expense.transaction_type == 'Debit':
                    balance.current_balance += amount  # Add back debited amount
                    balance.total_debits -= amount
                else:  # Credit
                    balance.current_balance -= amount  # Subtract credited amount
                    balance.total_credits -= amount
                balance.last_updated = datetime.utcnow()
            
            # Delete the transaction record
            db.session.delete(expense)
            db.session.commit()
            
            return True, "Transaction deleted and balance reversed."
        
        except Exception as e:
            db.session.rollback()
            return False, f"Error deleting transaction: {str(e)}"
    
    def get_auto_detected_transactions(
        self,
        user_id: int,
        month: Optional[int] = None,
        year: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[list, int]:
        """
        Get auto-detected transactions for a user
        
        Args:
            user_id: User ID
            month: Optional month filter (1-12)
            year: Optional year filter
            limit: Max results to return
            offset: Offset for pagination
        
        Returns:
            Tuple of (transactions: List[Dict], total_count: int)
        """
        query = Expense.query.filter_by(
            user_id=user_id,
            is_auto_detected=True
        )
        
        if month and year:
            query = query.filter(
                db.extract('month', Expense.date) == month,
                db.extract('year', Expense.date) == year
            )
        
        total_count = query.count()
        
        transactions = query.order_by(
            Expense.date.desc()
        ).limit(limit).offset(offset).all()
        
        return [t.to_dict() for t in transactions], total_count
    
    def get_transaction_statistics(self, user_id: int) -> Dict:
        """
        Get statistics about user's transactions (auto vs manual)
        
        Args:
            user_id: User ID
        
        Returns:
            Dict with statistics
        """
        from sqlalchemy import func
        from datetime import datetime
        
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        # Auto-detected expenses this month
        auto_expenses = db.session.query(func.sum(Expense.amount)).filter_by(
            user_id=user_id,
            is_auto_detected=True
        ).filter(
            db.extract('month', Expense.date) == current_month,
            db.extract('year', Expense.date) == current_year
        ).scalar() or 0.0
        
        # Manual expenses this month
        manual_expenses = db.session.query(func.sum(Expense.amount)).filter_by(
            user_id=user_id,
            is_auto_detected=False
        ).filter(
            db.extract('month', Expense.date) == current_month,
            db.extract('year', Expense.date) == current_year
        ).scalar() or 0.0
        
        # Count of transactions
        auto_count = Expense.query.filter_by(
            user_id=user_id,
            is_auto_detected=True
        ).filter(
            db.extract('month', Expense.date) == current_month,
            db.extract('year', Expense.date) == current_year
        ).count()
        
        manual_count = Expense.query.filter_by(
            user_id=user_id,
            is_auto_detected=False
        ).filter(
            db.extract('month', Expense.date) == current_month,
            db.extract('year', Expense.date) == current_year
        ).count()
        
        # Income
        total_income = db.session.query(func.sum(Income.amount)).filter_by(
            user_id=user_id
        ).filter(
            db.extract('month', Income.date) == current_month,
            db.extract('year', Income.date) == current_year
        ).scalar() or 0.0
        
        return {
            'auto_detected': {
                'amount': auto_expenses,
                'count': auto_count
            },
            'manual': {
                'amount': manual_expenses,
                'count': manual_count
            },
            'total_expenses': auto_expenses + manual_expenses,
            'total_income': total_income,
            'savings': total_income - (auto_expenses + manual_expenses)
        }


# Factory function
def get_transaction_service() -> TransactionService:
    """
    Factory function to get transaction service instance
    
    Returns:
        TransactionService: Initialized service instance
    """
    return TransactionService()
