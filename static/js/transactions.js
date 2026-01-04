/**
 * Transaction Messages JavaScript
 * Handles auto-detection and processing of transaction messages
 */

// Transaction Form Handler
function setupTransactionFormHandlers() {
    const form = document.getElementById('transactionMessageForm');
    if (form) {
        form.addEventListener('submit', handleProcessTransactionMessage);
    }
}

async function handleProcessTransactionMessage(e) {
    e.preventDefault();
    
    const messageText = document.getElementById('transactionMessage').value.trim();
    
    if (!messageText) {
        showNotification('Please enter a transaction message', 'error');
        return;
    }
    
    const statusEl = document.getElementById('processingStatus');
    statusEl.textContent = 'Processing message with AI...';
    statusEl.setAttribute('role', 'status');
    statusEl.setAttribute('aria-live', 'polite');
    statusEl.className = 'status-message';
    statusEl.classList.remove('hidden');
    
    try {
        const response = await fetch('/api/transactions/upload-message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: messageText
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            statusEl.className = 'status-message success';
            statusEl.innerHTML = `
                <strong>✅ Success!</strong><br>
                ${result.message}<br>
                <small>Balance Updated: ${formatCurrency(result.balance.current_balance)}</small>
            `;
            
            // Clear form
            document.getElementById('transactionMessage').value = '';
            
            // Reload transaction lists
            await loadAutoTransactions();
            await loadBalance();
            await loadTransactionStatistics();
            
            // Auto-hide success message after 5 seconds
            setTimeout(() => {
                statusEl.classList.add('hidden');
            }, 5000);
        } else {
            statusEl.className = 'status-message error';
            statusEl.innerHTML = `<strong>❌ Error!</strong><br>${result.message}`;
        }
    } catch (error) {
        console.error('Error processing transaction:', error);
        statusEl.className = 'status-message error';
        statusEl.innerHTML = `<strong>❌ Error!</strong><br>Failed to process message. Please try again.`;
    }
}

async function loadAutoTransactions() {
    try {
        const currentMonth = new Date().getMonth() + 1;
        const currentYear = new Date().getFullYear();
        
        const response = await fetch(
            `/api/transactions/auto?month=${currentMonth}&year=${currentYear}&limit=50`
        );
        const result = await response.json();
        
        const container = document.getElementById('autoTransactionsList');
        
        if (!result.transactions || result.transactions.length === 0) {
            container.innerHTML = '<p class="empty-state">No auto-detected transactions yet.</p>';
            return;
        }
        
        let html = '';
        result.transactions.forEach(transaction => {
            const typeClass = transaction.transaction_type === 'Debit' ? 'debit' : 'credit';
            const typeEmoji = transaction.transaction_type === 'Debit' ? '💸' : '💰';
            const amountClass = transaction.transaction_type === 'Debit' ? 'debit' : 'credit';
            const amountSign = transaction.transaction_type === 'Debit' ? '−' : '+';
            
            html += `
                <div class="transaction-item ${typeClass}">
                    <div class="transaction-info">
                        <div class="transaction-header">
                            <span class="transaction-type-badge ${typeClass}">
                                ${typeEmoji} ${transaction.transaction_type}
                            </span>
                            <span class="transaction-auto-badge">🤖 Auto</span>
                        </div>
                        <div class="transaction-merchant">${escapeHtml(transaction.merchant_or_source)}</div>
                        <div class="transaction-category">Category: ${transaction.category}</div>
                        <div class="transaction-date" style="font-size: 12px; color: #999; margin-top: 4px;">
                            ${new Date(transaction.date).toLocaleDateString()}
                        </div>
                    </div>
                    <div class="transaction-amount ${amountClass}">
                        ${amountSign}${formatCurrency(transaction.amount)}
                    </div>
                    <div class="transaction-actions">
                        <button class="btn-edit" onclick="editTransaction(${transaction.id})">✏️ Edit</button>
                        <button class="btn-delete" onclick="deleteTransaction(${transaction.id})">🗑️ Delete</button>
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
    } catch (error) {
        console.error('Error loading auto transactions:', error);
        document.getElementById('autoTransactionsList').innerHTML = 
            '<p class="empty-state">Error loading transactions</p>';
    }
}

async function loadBalance() {
    try {
        const response = await fetch('/api/balance/current');
        const result = await response.json();
        
        if (result.success) {
            const balance = result.balance;
            
            // Update balance display in header using data-amount
            const headerBalance = document.querySelector('.balance-display strong [data-amount]');
            if (headerBalance) {
                headerBalance.setAttribute('data-amount', Number(balance.current_balance || 0));
            }
            
            // Update balance summary card
            const balanceAmountEl = document.querySelector('#balanceAmount [data-amount]');
            const totalCreditsEl = document.querySelector('#totalCredits [data-amount]');
            const totalDebitsEl = document.querySelector('#totalDebits [data-amount]');
            const netFlowEl = document.querySelector('#netFlow [data-amount]');

            if (balanceAmountEl) balanceAmountEl.setAttribute('data-amount', Number(balance.current_balance || 0));
            if (totalCreditsEl) totalCreditsEl.setAttribute('data-amount', Number(balance.total_credits || 0));
            if (totalDebitsEl) totalDebitsEl.setAttribute('data-amount', Number(balance.total_debits || 0));

            const netFlow = (balance.total_credits || 0) - (balance.total_debits || 0);
            if (netFlowEl) netFlowEl.setAttribute('data-amount', Number(netFlow || 0));

            // Refresh formatting if CurrencyManager available
            if (window.CurrencyManager && typeof window.CurrencyManager.updateAllAmounts === 'function') {
                window.CurrencyManager.updateAllAmounts();
            } else {
                if (balanceAmountEl) balanceAmountEl.textContent = `₹${(balance.current_balance||0).toFixed(2)}`;
                if (totalCreditsEl) totalCreditsEl.textContent = `₹${(balance.total_credits||0).toFixed(2)}`;
                if (totalDebitsEl) totalDebitsEl.textContent = `₹${(balance.total_debits||0).toFixed(2)}`;
                if (netFlowEl) netFlowEl.textContent = `₹${netFlow.toFixed(2)}`;
            }
            
            // Color net flow
            const netFlowWrapper = document.getElementById('netFlow');
            if (netFlowWrapper) netFlowWrapper.style.color = netFlow >= 0 ? '#48bb78' : '#f56565';
        }
    } catch (error) {
        console.error('Error loading balance:', error);
    }
}

async function loadTransactionStatistics() {
    try {
        const response = await fetch('/api/balance/statistics');
        const result = await response.json();
        
        if (result.success) {
            const stats = result.statistics;
            
            // Update statistics display
            document.getElementById('autoCount').textContent = stats.auto_detected.count;
            document.getElementById('autoAmount').textContent = `₹${stats.auto_detected.amount.toFixed(2)}`;
            
            document.getElementById('manualCount').textContent = stats.manual.count;
            document.getElementById('manualAmount').textContent = `₹${stats.manual.amount.toFixed(2)}`;
            
            document.getElementById('totalExpensesStats').textContent = 
                `₹${stats.total_expenses.toFixed(2)}`;
            document.getElementById('totalIncomeStats').textContent = 
                `₹${stats.total_income.toFixed(2)}`;
        }
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

async function editTransaction(transactionId) {
    const newAmount = prompt('Enter new amount:');
    if (!newAmount) return;
    
    try {
        const response = await fetch(`/api/transactions/${transactionId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                amount: parseFloat(newAmount)
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('Transaction updated successfully', 'success');
            await loadAutoTransactions();
            await loadBalance();
            await loadTransactionStatistics();
        } else {
            showNotification(result.message || 'Failed to update transaction', 'error');
        }
    } catch (error) {
        console.error('Error editing transaction:', error);
        showNotification('Error updating transaction', 'error');
    }
}

async function deleteTransaction(transactionId) {
    if (!confirm('Are you sure you want to delete this transaction? The balance will be reversed.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/transactions/${transactionId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('Transaction deleted and balance reversed', 'success');
            await loadAutoTransactions();
            await loadBalance();
            await loadTransactionStatistics();
        } else {
            showNotification(result.message || 'Failed to delete transaction', 'error');
        }
    } catch (error) {
        console.error('Error deleting transaction:', error);
        showNotification('Error deleting transaction', 'error');
    }
}

// Initialize transaction section when showing it
function initializeTransactionSection() {
    setupTransactionFormHandlers();
    loadAutoTransactions();
    loadBalance();
    loadTransactionStatistics();
}
