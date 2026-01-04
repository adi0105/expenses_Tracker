/* Dashboard Application Logic */

let categoryChart = null;
let trendChart = null;
let comparisonChart = null;

/**
 * Initialize dashboard on page load
 */
document.addEventListener('DOMContentLoaded', async () => {
    await initDashboard();
    setupEventListeners();
});

/**
 * Initialize dashboard data and UI
 */
async function initDashboard() {
    const monthSelect = document.getElementById('monthSelect');

    // Load initial data
    await loadMonthlySummary();

    // Load lists
    await loadExpensesList();
    await loadIncomeList();

    // Set up month change listener
    monthSelect.addEventListener('change', () => {
        loadMonthlySummary();
    });
}

/**
 * Setup event listeners for navigation and forms
 */
function setupEventListeners() {
    // Navigation links
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const section = link.getAttribute('data-section');
            showSection(section);

            // Update active state
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
        });
    });

    // Add expense button
    document.getElementById('addExpenseBtn')?.addEventListener('click', () => {
        toggleForm('expenseForm');
        setDateToToday('expenseDate');
    });

    // Add income button
    document.getElementById('addIncomeBtn')?.addEventListener('click', () => {
        toggleForm('incomeForm');
        setDateToToday('incomeDate');
    });

    // Expense form submission
    document.getElementById('expenseSubmitForm')?.addEventListener('submit', handleAddExpense);

    // Income form submission
    document.getElementById('incomeSubmitForm')?.addEventListener('submit', handleAddIncome);

    // AI Classify button
    document.getElementById('aiClassifyBtn')?.addEventListener('click', handleAIClassify);

    // Generate insights button
    document.getElementById('generateInsightsBtn')?.addEventListener('click', handleGenerateInsights);
}

/**
 * Show specific section
 */
function showSection(sectionName) {
    // Hide all sections
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => {
        section.classList.remove('active');
    });

    // Show selected section
    const section = document.getElementById(sectionName);
    if (section) {
        section.classList.add('active');
    }

    // Update section title
    const titles = {
        overview: 'Overview',
        transactions: 'Transaction Messages',
        expenses: 'Manage Expenses',
        income: 'Manage Income',
        insights: 'AI Financial Insights',
        analytics: 'Financial Analytics'
    };

    document.getElementById('sectionTitle').textContent = titles[sectionName] || 'Dashboard';

    // Load section-specific data
    if (sectionName === 'analytics') {
        loadAnalyticsCharts();
    } else if (sectionName === 'transactions') {
        initializeTransactionSection();
    }
}

/**
 * Load monthly summary data
 */
async function loadMonthlySummary() {
    try {
        const monthSelect = document.getElementById('monthSelect');
        const selectedValue = JSON.parse(monthSelect.value || '{}');
        const month = selectedValue.month || new Date().getMonth() + 1;
        const year = selectedValue.year || new Date().getFullYear();

        const response = await fetch(`/api/summary/monthly?month=${month}&year=${year}`);
        const data = await response.json();

        if (data.success) {
            // Update summary cards using data-amount so CurrencyManager can apply symbol
            const totalIncomeEl = document.querySelector('#totalIncome [data-amount]');
            const totalExpensesEl = document.querySelector('#totalExpenses [data-amount]');
            const totalSavingsEl = document.querySelector('#totalSavings [data-amount]');

            if (totalIncomeEl) {
                totalIncomeEl.setAttribute('data-amount', Number(data.total_income || 0));
            }
            if (totalExpensesEl) {
                totalExpensesEl.setAttribute('data-amount', Number(data.total_expenses || 0));
            }
            if (totalSavingsEl) {
                totalSavingsEl.setAttribute('data-amount', Number(data.savings || 0));
            }

            // If CurrencyManager is available, refresh formatting, otherwise fallback
            if (window.CurrencyManager && typeof window.CurrencyManager.updateAllAmounts === 'function') {
                window.CurrencyManager.updateAllAmounts();
            } else {
                if (totalIncomeEl) totalIncomeEl.textContent = formatCurrency(data.total_income);
                if (totalExpensesEl) totalExpensesEl.textContent = formatCurrency(data.total_expenses);
                if (totalSavingsEl) totalSavingsEl.textContent = formatCurrency(data.savings);
            }

            // Calculate savings percentage
            const savingsPercent = data.total_income > 0
                ? ((data.savings / data.total_income) * 100).toFixed(1)
                : 0;
            document.getElementById('savingsPercent').textContent = `${savingsPercent}% saved`;

            // Update category chart
            updateCategoryChart(data.expenses_by_category);
            // Announce update for screen reader users
            if (typeof showNotification === 'function') showNotification('Monthly summary updated', 'info');
        }
    } catch (error) {
        console.error('Error loading summary:', error);
        showNotification('Failed to load summary', 'error');
    }
}

/**
 * Update category breakdown chart
 */
function updateCategoryChart(categoryData) {
    const ctx = document.getElementById('categoryChart');
    if (!ctx) return;

    const labels = Object.keys(categoryData);
    const values = Object.values(categoryData);

    // Destroy existing chart
    if (categoryChart) {
        categoryChart.destroy();
    }

    categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    '#667eea',
                    '#764ba2',
                    '#f56565',
                    '#ed8936',
                    '#ecc94b',
                    '#38a169',
                    '#4299e1',
                ],
                borderColor: '#fff',
                borderWidth: 2,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return formatCurrency(context.parsed);
                        }
                    }
                }
            }
        }
    });
}

/**
 * Load expenses list
 */
async function loadExpensesList() {
    try {
        const response = await fetch('/api/expenses/list?limit=50');
        const data = await response.json();

        const expensesList = document.getElementById('expensesList');
        if (!expensesList) return;

        if (!data.success || data.expenses.length === 0) {
            expensesList.innerHTML = '<p class="empty-state">No expenses yet. Add one to get started!</p>';
            document.getElementById('expenseCount').textContent = '0 transactions';
            return;
        }

        document.getElementById('expenseCount').textContent = `${data.count} transactions`;

        const html = data.expenses.map(expense => `
            <div class="transaction-item">
                <div class="transaction-info">
                    <div class="transaction-title">${escapeHtml(expense.description)}</div>
                    <div class="transaction-meta">
                        ${expense.category} • ${formatDate(expense.date)}
                        ${expense.ai_classified ? ' 🤖' : ''}
                    </div>
                </div>
                <div class="transaction-amount" style="color: #f56565;">
                    <span class="sign">−</span><span data-amount="${expense.amount}">${formatCurrency(expense.amount)}</span>
                </div>
                <div class="transaction-actions">
                    <button onclick="deleteExpense(${expense.id})" title="Delete">🗑️</button>
                </div>
            </div>
        `).join('');

        expensesList.innerHTML = html;
        if (window.CurrencyManager && typeof window.CurrencyManager.updateAllAmounts === 'function') window.CurrencyManager.updateAllAmounts();
        if (typeof showNotification === 'function') showNotification('Expenses list updated', 'info');
    } catch (error) {
        console.error('Error loading expenses:', error);
        showNotification('Failed to load expenses', 'error');
    }
}

/**
 * Load income list
 */
async function loadIncomeList() {
    try {
        const response = await fetch('/api/incomes/list?limit=50');
        const data = await response.json();

        const incomeList = document.getElementById('incomeList');
        if (!incomeList) return;

        if (!data.success || data.incomes.length === 0) {
            incomeList.innerHTML = '<p class="empty-state">No income recorded yet.</p>';
            document.getElementById('incomeCount').textContent = '0 sources';
            return;
        }

        document.getElementById('incomeCount').textContent = `${data.count} sources`;

        const html = data.incomes.map(income => `
            <div class="transaction-item">
                <div class="transaction-info">
                    <div class="transaction-title">${escapeHtml(income.source)}</div>
                    <div class="transaction-meta">
                        ${formatDate(income.date)}
                    </div>
                </div>
                <div class="transaction-amount" style="color: #48bb78;">
                    <span class="sign">+</span><span data-amount="${income.amount}">${formatCurrency(income.amount)}</span>
                </div>
                <div class="transaction-actions">
                    <button onclick="deleteIncome(${income.id})" title="Delete">🗑️</button>
                </div>
            </div>
        `).join('');

        incomeList.innerHTML = html;
        if (window.CurrencyManager && typeof window.CurrencyManager.updateAllAmounts === 'function') window.CurrencyManager.updateAllAmounts();
        if (typeof showNotification === 'function') showNotification('Income list updated', 'info');
    } catch (error) {
        console.error('Error loading income:', error);
        showNotification('Failed to load income', 'error');
    }
}

/**
 * Handle add expense form submission
 */
async function handleAddExpense(e) {
    e.preventDefault();

    const amount = document.getElementById('expenseAmount').value;
    const description = document.getElementById('expenseDescription').value;
    const category = document.getElementById('expenseCategory').value;
    const date = document.getElementById('expenseDate').value;

    if (!amount || !description || !date) {
        showNotification('Please fill in all required fields', 'warning');
        return;
    }

    try {
        const response = await fetch('/api/expenses/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                amount: parseFloat(amount),
                description,
                category: category || null,
                date,
                ai_classify: !category // Auto-classify if no category selected
            })
        });

        const data = await response.json();

        if (data.success) {
            showNotification('Expense added successfully!', 'success');
            document.getElementById('expenseSubmitForm').reset();
            toggleForm('expenseForm');
            await loadExpensesList();
            await loadMonthlySummary();
        } else {
            showNotification(data.message || 'Failed to add expense', 'error');
        }
    } catch (error) {
        console.error('Error adding expense:', error);
        showNotification('Failed to add expense', 'error');
    }
}

/**
 * Handle add income form submission
 */
async function handleAddIncome(e) {
    e.preventDefault();

    const amount = document.getElementById('incomeAmount').value;
    const source = document.getElementById('incomeSource').value;
    const date = document.getElementById('incomeDate').value;

    if (!amount || !source || !date) {
        showNotification('Please fill in all required fields', 'warning');
        return;
    }

    try {
        const response = await fetch('/api/incomes/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                amount: parseFloat(amount),
                source,
                date
            })
        });

        const data = await response.json();

        if (data.success) {
            showNotification('Income added successfully!', 'success');
            document.getElementById('incomeSubmitForm').reset();
            toggleForm('incomeForm');
            await loadIncomeList();
            await loadMonthlySummary();
        } else {
            showNotification(data.message || 'Failed to add income', 'error');
        }
    } catch (error) {
        console.error('Error adding income:', error);
        showNotification('Failed to add income', 'error');
    }
}

/**
 * Handle AI expense classification
 */
async function handleAIClassify() {
    const description = document.getElementById('expenseDescription').value;

    if (!description) {
        showNotification('Please enter an expense description first', 'warning');
        return;
    }

    try {
        const btn = document.getElementById('aiClassifyBtn');
        btn.textContent = '⏳ Classifying...';
        btn.disabled = true;

        const response = await fetch('/api/expenses/classify', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ description })
        });

        const data = await response.json();

        if (data.success) {
            document.getElementById('expenseCategory').value = data.category;
            showNotification(`Classified as: ${data.category}`, 'success');
        } else {
            showNotification('Failed to classify expense', 'error');
        }
    } catch (error) {
        console.error('Classification error:', error);
        showNotification('Classification failed', 'error');
    } finally {
        const btn = document.getElementById('aiClassifyBtn');
        btn.textContent = '🤖 Auto-Classify';
        btn.disabled = false;
    }
}

/**
 * Handle generate AI insights
 */
async function handleGenerateInsights() {
    try {
        const monthSelect = document.getElementById('monthSelect');
        const selectedValue = JSON.parse(monthSelect.value || '{}');
        const month = selectedValue.month || new Date().getMonth() + 1;
        const year = selectedValue.year || new Date().getFullYear();

        const btn = document.getElementById('generateInsightsBtn');
        btn.textContent = '⏳ Generating...';
        btn.disabled = true;

        const response = await fetch(`/api/summary/ai-insights?month=${month}&year=${year}`);
        const data = await response.json();

        if (data.success) {
            const container = document.getElementById('insightsContainer');
            container.textContent = data.insights;
            showNotification('Insights generated successfully!', 'success');
        } else {
            showNotification(data.message || 'Failed to generate insights', 'error');
        }
    } catch (error) {
        console.error('Error generating insights:', error);
        showNotification('Failed to generate insights', 'error');
    } finally {
        const btn = document.getElementById('generateInsightsBtn');
        btn.textContent = '🤖 Generate Insights';
        btn.disabled = false;
    }
}

/**
 * Delete expense
 */
async function deleteExpense(expenseId) {
    if (!confirm('Are you sure you want to delete this expense?')) {
        return;
    }

    try {
        const response = await fetch(`/api/expenses/${expenseId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            showNotification('Expense deleted successfully', 'success');
            await loadExpensesList();
            await loadMonthlySummary();
        } else {
            showNotification('Failed to delete expense', 'error');
        }
    } catch (error) {
        console.error('Error deleting expense:', error);
        showNotification('Failed to delete expense', 'error');
    }
}

/**
 * Delete income
 */
async function deleteIncome(incomeId) {
    if (!confirm('Are you sure you want to delete this income record?')) {
        return;
    }

    try {
        const response = await fetch(`/api/incomes/${incomeId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            showNotification('Income deleted successfully', 'success');
            await loadIncomeList();
            await loadMonthlySummary();
        } else {
            showNotification('Failed to delete income', 'error');
        }
    } catch (error) {
        console.error('Error deleting income:', error);
        showNotification('Failed to delete income', 'error');
    }
}

/**
 * Load analytics charts
 */
async function loadAnalyticsCharts() {
    try {
        const year = new Date().getFullYear();
        const response = await fetch(`/api/summary/yearly?year=${year}`);
        const data = await response.json();

        if (data.success) {
            updateTrendChart(data.monthly_breakdown);
            updateComparisonChart(data.monthly_breakdown);
        }
    } catch (error) {
        console.error('Error loading analytics:', error);
        showNotification('Failed to load analytics', 'error');
    }
}

/**
 * Update trend chart
 */
function updateTrendChart(monthlyData) {
    const ctx = document.getElementById('trendChart');
    if (!ctx) return;

    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const expenses = monthlyData.map(d => d.expenses);
    const savings = monthlyData.map(d => d.savings);

    if (trendChart) {
        trendChart.destroy();
    }

    trendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: months,
            datasets: [
                {
                    label: 'Expenses',
                    data: expenses,
                    borderColor: '#f56565',
                    backgroundColor: 'rgba(245, 101, 101, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Savings',
                    data: savings,
                    borderColor: '#48bb78',
                    backgroundColor: 'rgba(72, 187, 120, 0.1)',
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

/**
 * Update comparison chart
 */
function updateComparisonChart(monthlyData) {
    const ctx = document.getElementById('comparisonChart');
    if (!ctx) return;

    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const income = monthlyData.map(d => d.income);
    const expenses = monthlyData.map(d => d.expenses);

    if (comparisonChart) {
        comparisonChart.destroy();
    }

    comparisonChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: months,
            datasets: [
                {
                    label: 'Income',
                    data: income,
                    backgroundColor: '#48bb78'
                },
                {
                    label: 'Expenses',
                    data: expenses,
                    backgroundColor: '#f56565'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
