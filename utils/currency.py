"""
Currency Utility Module
Handles currency formatting, conversion, and symbols
"""

# Supported currencies with symbols
CURRENCIES = {
    'INR': {'symbol': '₹', 'name': 'Indian Rupee', 'flag': '🇮🇳'},
    'USD': {'symbol': '$', 'name': 'US Dollar', 'flag': '🇺🇸'},
    'EUR': {'symbol': '€', 'name': 'Euro', 'flag': '🇪🇺'},
    'GBP': {'symbol': '£', 'name': 'British Pound', 'flag': '🇬🇧'},
    'JPY': {'symbol': '¥', 'name': 'Japanese Yen', 'flag': '🇯🇵'},
    'AUD': {'symbol': 'A$', 'name': 'Australian Dollar', 'flag': '🇦🇺'},
    'CAD': {'symbol': 'C$', 'name': 'Canadian Dollar', 'flag': '🇨🇦'},
    'CHF': {'symbol': 'Fr', 'name': 'Swiss Franc', 'flag': '🇨🇭'},
    'CNY': {'symbol': '¥', 'name': 'Chinese Yuan', 'flag': '🇨🇳'},
    'SGD': {'symbol': 'S$', 'name': 'Singapore Dollar', 'flag': '🇸🇬'},
    'HKD': {'symbol': 'HK$', 'name': 'Hong Kong Dollar', 'flag': '🇭🇰'},
    'AED': {'symbol': 'د.إ', 'name': 'UAE Dirham', 'flag': '🇦🇪'},
}

# Approximate exchange rates to INR (base currency)
# Update these periodically from real API
EXCHANGE_RATES = {
    'INR': 1.0,
    'USD': 83.5,
    'EUR': 91.2,
    'GBP': 105.3,
    'JPY': 0.56,
    'AUD': 54.8,
    'CAD': 61.5,
    'CHF': 93.2,
    'CNY': 11.5,
    'SGD': 62.1,
    'HKD': 10.65,
    'AED': 22.75,
}


def get_currency_symbol(currency_code: str) -> str:
    """
    Get the symbol for a currency code
    
    Args:
        currency_code: ISO 4217 code (e.g., 'INR', 'USD')
    
    Returns:
        str: Currency symbol
    """
    if currency_code in CURRENCIES:
        return CURRENCIES[currency_code]['symbol']
    return currency_code


def format_amount(amount: float, currency_code: str = 'INR', decimals: int = 2) -> str:
    """
    Format an amount with currency symbol
    
    Args:
        amount: Numeric amount
        currency_code: ISO 4217 code (default: INR)
        decimals: Number of decimal places (default: 2)
    
    Returns:
        str: Formatted string (e.g., '₹1,234.56')
    """
    if not currency_code or currency_code not in CURRENCIES:
        currency_code = 'INR'
    
    symbol = CURRENCIES[currency_code]['symbol']
    
    # Format with thousands separator and specified decimals
    formatted = f"{amount:,.{decimals}f}"
    
    return f"{symbol}{formatted}"


def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str
) -> float:
    """
    Convert amount from one currency to another using cached rates
    
    Args:
        amount: Amount to convert
        from_currency: Source currency code
        to_currency: Target currency code
    
    Returns:
        float: Converted amount
    """
    if from_currency == to_currency:
        return amount
    
    if from_currency not in EXCHANGE_RATES or to_currency not in EXCHANGE_RATES:
        return amount  # No conversion if rate not found
    
    # Convert to INR as base, then to target
    amount_in_inr = amount * EXCHANGE_RATES[from_currency]
    converted_amount = amount_in_inr / EXCHANGE_RATES[to_currency]
    
    return round(converted_amount, 2)


def get_currency_list() -> list:
    """
    Get list of all supported currencies with metadata
    
    Returns:
        list: List of dicts with code, symbol, name, flag
    """
    currencies = []
    for code, info in CURRENCIES.items():
        currencies.append({
            'code': code,
            'symbol': info['symbol'],
            'name': info['name'],
            'flag': info['flag']
        })
    return sorted(currencies, key=lambda x: x['name'])


def validate_currency(currency_code: str) -> bool:
    """
    Validate if a currency code is supported
    
    Args:
        currency_code: ISO 4217 code to validate
    
    Returns:
        bool: True if supported, False otherwise
    """
    return currency_code in CURRENCIES


def get_currency_info(currency_code: str) -> dict:
    """
    Get full information about a currency
    
    Args:
        currency_code: ISO 4217 code
    
    Returns:
        dict: Currency info with symbol, name, flag
    """
    if currency_code not in CURRENCIES:
        return {}
    
    return {
        'code': currency_code,
        **CURRENCIES[currency_code]
    }
