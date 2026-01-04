"""
LLM Integration Service Module
Handles all interactions with OpenAI API for expense classification and insights

This service implements:
1. Expense classification using AI
2. Monthly financial insights generation
3. Prompt engineering for optimal results
"""

import os
import json
import requests
from typing import Optional, Dict, List
from datetime import datetime


class LLMService:
    """
    Service for integrating with OpenAI API for AI-powered financial features
    
    Features:
    - Classify expenses into predefined categories
    - Generate monthly financial insights
    - Prompt engineering for optimal LLM responses
    """
    
    EXPENSE_CATEGORIES = ['Food', 'Travel', 'Shopping', 'Bills', 'Entertainment', 'Health', 'Other']
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize LLM Service
        
        Args:
            api_key: OpenAI API key. Uses OPENAI_API_KEY env var if not provided
        """
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        self.model = os.environ.get('LLM_MODEL', 'gpt-3.5-turbo')
        self.api_endpoint = 'https://api.openai.com/v1/chat/completions'
        
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
    
    def _make_api_call(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """
        Make API call to OpenAI
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
        
        Returns:
            str: Response content from API, or None if error
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': self.model,
                'messages': messages,
                'temperature': 0.7,
                'max_tokens': 500
            }
            
            response = requests.post(
                self.api_endpoint,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            return None
        except (KeyError, json.JSONDecodeError) as e:
            print(f"Response Parsing Error: {e}")
            return None
    
    def classify_expense(self, expense_description: str) -> Optional[str]:
        """
        Classify expense into one of the predefined categories using AI
        
        Uses prompt engineering to ensure accurate classification
        
        Args:
            expense_description: Description of the expense
        
        Returns:
            str: Classified category or None if classification fails
        
        Example:
            >>> service = LLMService()
            >>> category = service.classify_expense("Bought lunch at McDonald's")
            >>> print(category)  # Output: 'Food'
        """
        
        # Construct the classification prompt
        prompt = f"""You are an intelligent finance assistant.
Classify the following expense into one category only:
Food, Travel, Shopping, Bills, Entertainment, Health, Other.

Expense description: {expense_description}

Return only the category name."""
        
        messages = [
            {
                'role': 'system',
                'content': 'You are a financial categorization expert. Return only the category name.'
            },
            {
                'role': 'user',
                'content': prompt
            }
        ]
        
        response = self._make_api_call(messages)
        
        if response:
            # Clean the response to get the category
            response = response.strip().title()
            
            # Validate that response is in valid categories
            if response in self.EXPENSE_CATEGORIES:
                return response
            else:
                # Try to find a matching category
                for category in self.EXPENSE_CATEGORIES:
                    if category.lower() in response.lower():
                        return category
                return 'Other'
        
        return None
    
    def generate_monthly_insights(self, expense_data: Dict) -> Optional[str]:
        """
        Generate personalized monthly financial insights using AI
        
        Args:
            expense_data: Dictionary containing:
                - total_expenses: Total amount spent
                - total_income: Total income
                - expenses_by_category: Dict of categories and amounts
                - expense_count: Number of expenses
                - month: Month name
                - year: Year
        
        Returns:
            str: AI-generated insights or None if generation fails
        
        Example:
            >>> expense_data = {
            ...     'total_expenses': 2500,
            ...     'total_income': 5000,
            ...     'expenses_by_category': {'Food': 600, 'Transport': 300, ...},
            ...     'month': 'January',
            ...     'year': 2024
            ... }
            >>> insights = service.generate_monthly_insights(expense_data)
            >>> print(insights)
        """
        
        # Format expense data for the prompt
        json_expense_data = json.dumps(expense_data, indent=2)
        
        prompt = f"""You are a personal finance advisor.

Based on the user's monthly expense data below, generate:
1. Total spending summary
2. Top 3 spending categories
3. Spending behavior analysis
4. 3 personalized money-saving tips

Expense Data:
{json_expense_data}

Keep the response concise, practical, and user-friendly."""
        
        messages = [
            {
                'role': 'system',
                'content': 'You are a helpful personal finance advisor providing actionable insights based on spending data.'
            },
            {
                'role': 'user',
                'content': prompt
            }
        ]
        
        return self._make_api_call(messages)
    
    def get_spending_advice(self, category: str, amount: float) -> Optional[str]:
        """
        Get AI-powered advice for a specific category
        
        Args:
            category: Expense category
            amount: Amount spent in this category
        
        Returns:
            str: Personalized advice or None if generation fails
        """
        
        prompt = f"""You are a personal finance advisor. 
The user spent ${amount:.2f} on {category} this month.
Provide 2-3 practical, specific tips to reduce spending in this category while maintaining quality of life.
Keep the response brief and actionable."""
        
        messages = [
            {
                'role': 'system',
                'content': 'You are a practical personal finance advisor providing specific money-saving tips.'
            },
            {
                'role': 'user',
                'content': prompt
            }
        ]
        
        return self._make_api_call(messages)
    
    def parse_transaction_message(self, transaction_message: str) -> Optional[Dict]:
        """
        Parse transaction message (SMS/alert) to extract financial details using AI
        
        Uses prompt engineering to extract:
        - Transaction type (Credit/Debit)
        - Amount
        - Merchant/Source
        - Expense category
        
        Args:
            transaction_message: Raw transaction message text
            Example: "₹2,500 debited from your account via UPI at Amazon"
        
        Returns:
            Dict with keys: transaction_type, amount, merchant_or_source, expense_category
            Returns None if parsing fails
        
        Example:
            >>> service = LLMService()
            >>> result = service.parse_transaction_message("₹2,500 debited from your account via UPI at Amazon")
            >>> print(result)
            {
                "transaction_type": "Debit",
                "amount": 2500,
                "merchant_or_source": "Amazon",
                "expense_category": "Shopping"
            }
        """
        
        # Use the exact prompt from requirements
        system_prompt = """You are a financial transaction parser.

Extract the following details from the message below:
- transaction_type: Credit or Debit
- amount (number only)
- merchant_or_source
- expense_category (Food, Travel, Shopping, Bills, Entertainment, Health, Other)

Return the output strictly in JSON format only, no other text."""
        
        user_message = f"""Transaction Message:
{transaction_message}

Return ONLY valid JSON in this format:
{{
  "transaction_type": "Debit",
  "amount": 2500,
  "merchant_or_source": "Amazon",
  "expense_category": "Shopping"
}}"""
        
        messages = [
            {
                'role': 'system',
                'content': system_prompt
            },
            {
                'role': 'user',
                'content': user_message
            }
        ]
        
        response = self._make_api_call(messages)
        
        if not response:
            return None
        
        try:
            # Parse JSON response
            parsed = json.loads(response)
            
            # Validate required fields
            required_fields = ['transaction_type', 'amount', 'merchant_or_source', 'expense_category']
            if not all(field in parsed for field in required_fields):
                print("Missing required fields in LLM response")
                return None
            
            # Validate transaction type
            if parsed['transaction_type'] not in ['Credit', 'Debit']:
                print(f"Invalid transaction type: {parsed['transaction_type']}")
                return None
            
            # Validate and convert amount to float
            try:
                parsed['amount'] = float(parsed['amount'])
                if parsed['amount'] <= 0:
                    print("Amount must be positive")
                    return None
            except (ValueError, TypeError):
                print(f"Invalid amount: {parsed['amount']}")
                return None
            
            # Validate category
            valid_categories = self.EXPENSE_CATEGORIES
            if parsed['expense_category'] not in valid_categories:
                print(f"Invalid category: {parsed['expense_category']}")
                parsed['expense_category'] = 'Other'
            
            return parsed
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse LLM JSON response: {e}")
            print(f"Response was: {response}")
            return None
    
    def generate_auto_vs_manual_insights(self, financial_data: Dict) -> Optional[str]:
        """
        Generate insights comparing auto-detected vs manual transactions
        
        Args:
            financial_data: Dictionary containing:
                - total_auto_transactions: Count of auto-detected
                - total_manual_transactions: Count of manual
                - total_income: Total income amount
                - total_expenses: Total expenses
                - auto_expense_total: Total from auto-detected
                - manual_expense_total: Total from manual
                - top_categories: Top spending categories
                - month: Month name
        
        Returns:
            str: Insights comparing auto vs manual entries
        """
        
        json_data = json.dumps(financial_data, indent=2)
        
        prompt = f"""You are a financial data analyst.

Analyze the user's transaction data with auto-detected vs manual entries:

{json_data}

Generate insights covering:
1. Overall spending summary
2. Auto-detected vs manual transaction breakdown
3. Key spending patterns and categories
4. 3 actionable money-saving tips specific to their spending habits
5. Recommendations on automating more transactions

Keep advice practical and beginner-friendly."""
        
        messages = [
            {
                'role': 'system',
                'content': 'You are a helpful financial advisor analyzing transaction patterns and providing practical insights.'
            },
            {
                'role': 'user',
                'content': prompt
            }
        ]
        
        return self._make_api_call(messages)



# Initialize service (can be imported directly)
def get_llm_service() -> LLMService:
    """
    Factory function to get LLM service instance
    
    Returns:
        LLMService: Initialized service instance
    """
    try:
        return LLMService()
    except ValueError as e:
        print(f"LLM Service initialization error: {e}")
        return None
