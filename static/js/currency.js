/**
 * Currency Formatting Module
 * Handles dynamic currency display throughout the dashboard
 */

const CurrencyManager = (() => {
    let currentCurrency = 'INR';
    let currencySymbols = {};
    
    // Currency symbols
    const symbols = {
        'INR': '₹',
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥',
        'AUD': 'A$',
        'CAD': 'C$',
        'CHF': 'Fr',
        'CNY': '¥',
        'SGD': 'S$',
        'HKD': 'HK$',
        'AED': 'د.إ'
    };
    
    // Initialize currency manager
    const init = () => {
        loadUserCurrency();
        observeMutations();
    };
    
    // Load user's preferred currency from API
    const loadUserCurrency = async () => {
        try {
            // Ensure cookies/session are sent for same-origin requests
            const response = await fetch('/api/settings/currency', { credentials: 'same-origin' });
            if (!response.ok) {
                // Try profile endpoint as a fallback which also contains currency info
                const prof = await fetch('/api/settings/profile', { credentials: 'same-origin' });
                if (prof.ok) {
                    const p = await prof.json();
                    if (p.success && p.user && p.user.preferred_currency) {
                        currentCurrency = p.user.preferred_currency;
                        if (p.user.preferred_currency_symbol) {
                            symbols[currentCurrency] = p.user.preferred_currency_symbol;
                        }
                        updateAllAmounts();
                        return;
                    }
                }
                throw new Error('Currency endpoints unavailable');
            }

            const data = await response.json();
            if (data && data.success) {
                currentCurrency = data.current_currency || currentCurrency;
                // If user has a custom symbol, override the default symbol for this currency
                if (data.custom_symbol) {
                    symbols[currentCurrency] = data.custom_symbol;
                }
                updateAllAmounts();
            }
        } catch (error) {
            console.warn('Could not load currency preference, falling back to defaults:', error);
            currentCurrency = 'INR';
            updateAllAmounts();
        }
    };
    
    // Format an amount with the current currency
    const format = (amount, decimals = 2) => {
        if (!amount && amount !== 0) return '--';
        
        const symbol = symbols[currentCurrency] || currentCurrency;
        const formatted = Number(amount).toLocaleString('en-IN', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        });
        
        return `${symbol}${formatted}`;
    };
    
    // Get current currency code
    const getCurrent = () => currentCurrency;
    
    // Get symbol for a currency
    const getSymbol = (code) => symbols[code] || code;
    
    // Update all amount displays on page
    const updateAllAmounts = () => {
        // Update balance displays
        const balanceElements = document.querySelectorAll('[data-amount]');
        balanceElements.forEach(el => {
            const amount = el.getAttribute('data-amount');
            if (amount) {
                el.textContent = format(parseFloat(amount));
            }
        });
        
        // Update currency symbol displays
        const symbolElements = document.querySelectorAll('[data-currency-symbol]');
        symbolElements.forEach(el => {
            el.textContent = getSymbol(currentCurrency);
        });
    };
    
    // Observer for dynamically added amounts
    const observeMutations = () => {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList' || mutation.type === 'attributes') {
                    updateAllAmounts();
                }
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['data-amount']
        });
    };
    
    // Public API
    return {
        init,
        format,
        getCurrent,
        getSymbol,
        updateAllAmounts,
        loadUserCurrency
    };
})();

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    CurrencyManager.init();
});
// Expose to window so other modules can call updateAllAmounts
if (typeof window !== 'undefined') {
    window.CurrencyManager = CurrencyManager;
}
