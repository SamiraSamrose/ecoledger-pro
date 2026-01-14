let tradingCharts = {};

// Refresh trading data
async function refreshTradingData() {
    try {
        await Promise.all([
            loadAvailablePortfolios(),
            loadRecentTrades(),
            loadTradingCharts()
        ]);
        showNotification('Trading data refreshed', 'success');
    } catch (error) {
        console.error('Error refreshing trading data:', error);
        showNotification('Error refreshing trading data', 'error');
    }
}

// Load available portfolios
async function loadAvailablePortfolios() {
    try {
        const response = await apiRequest('/portfolios?status=Listed');
        const portfolios = response.portfolios || [];
        
        const container = document.getElementById('availablePortfolios');
        if (!container) return;
        
        if (portfolios.length === 0) {
            container.innerHTML = '<p style="color: var(--text-secondary);">No portfolios available</p>';
            return;
        }
        
        container.innerHTML = portfolios.map(portfolio => `
            <div class="portfolio-card">
                <div class="portfolio-header">
                    <h4>${portfolio.portfolio_id}</h4>
                    <span class="status-badge status-verified">${portfolio.status}</span>
                </div>
                <div class="portfolio-details">
                    <div class="detail-row">
                        <span class="label">Seller:</span>
                        <span class="value">${portfolio.seller_id}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Loan Count:</span>
                        <span class="value">${portfolio.loan_count}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Total Value:</span>
                        <span class="value">${formatCurrency(portfolio.total_value)}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Portfolio Price:</span>
                        <span class="value">${formatCurrency(portfolio.portfolio_price)}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Yield:</span>
                        <span class="value">${formatPercentage(portfolio.portfolio_yield * 100, 2)}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">ESG Score:</span>
                        <span class="value">${formatNumber(portfolio.weighted_esg_score, 1)}</span>
                    </div>
                </div>
                <div class="portfolio-actions">
                    <button class="btn btn-primary" onclick="executeTrade('${portfolio.portfolio_id}')">
                        Execute Trade
                    </button>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading portfolios:', error);
    }
}

// Load recent trades
async function loadRecentTrades() {
    try {
        const response = await apiRequest('/trades');
        const trades = response.trades || [];
        
        const container = document.getElementById('recentTrades');
        if (!container) return;
        
        if (trades.length === 0) {
            container.innerHTML = '<p style="color: var(--text-secondary);">No recent trades</p>';
            return;
        }
        
        container.innerHTML = trades.slice(0, 10).map(trade => `
            <div class="portfolio-card">
                <div class="portfolio-header">
                    <h4>${trade.trade_id}</h4>
                    <span class="status-badge status-verified">${trade.status}</span>
                </div>
                <div class="portfolio-details">
                    <div class="detail-row">
                        <span class="label">Portfolio:</span>
                        <span class="value">${trade.portfolio_id}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Seller:</span>
                        <span class="value">${trade.seller_id}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Buyer:</span>
                        <span class="value">${trade.buyer_id}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Trade Price:</span>
                        <span class="value">${formatCurrency(trade.trade_price)}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Loan Count:</span>
                        <span class="value">${trade.loan_count}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Date:</span>
                        <span class="value">${new Date(trade.trade_timestamp).toLocaleString()}</span>
                    </div>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading trades:', error);
    }
}

// Execute trade
async function executeTrade(portfolioId) {
    const buyerId = prompt('Enter Buyer ID:');
    if (!buyerId) return;
    
    const tradePriceInput = prompt('Enter Trade Price (leave empty for default):');
    const tradePrice = tradePriceInput ? parseFloat(tradePriceInput) : null;
    
    try {
        const result = await apiRequest('/trades/execute', {
            method: 'POST',
            body: JSON.stringify({
                portfolio_id: portfolioId,
                buyer_id: buyerId,
                trade_price: tradePrice
            })
        });
        
        showNotification('Trade executed successfully', 'success');
        await refreshTradingData();
        
    } catch (error) {
        console.error('Error executing trade:', error);
        showNotification(error.message || 'Error executing trade', 'error');
    }
}

// Handle create portfolio form submission
async function handleCreatePortfolioSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const sellerId = document.getElementById('portfolioSellerId').value;
    const loanIdsText = document.getElementById('portfolioLoanIds').value;
    
    const loanIds = loanIdsText.split(',').map(id => id.trim()).filter(id => id);
    
    if (loanIds.length === 0) {
        showNotification('Please provide at least one loan ID', 'error');
        return;
    }
    
    try {
        const result = await apiRequest('/portfolios/create', {
            method: 'POST',
            body: JSON.stringify({
                seller_id: sellerId,
                loan_ids: loanIds
            })
        });
        
        showNotification('Portfolio created successfully', 'success');
        closeModal('createPortfolioModal');
        form.reset();
        await refreshTradingData();
        
    } catch (error) {
        console.error('Error creating portfolio:', error);
        showNotification(error.message || 'Error creating portfolio', 'error');
    }
}

// Load trading charts
async function loadTradingCharts() {
    try {
        const [tradesResponse, portfoliosResponse] = await Promise.all([
            apiRequest('/trades'),
            apiRequest('/portfolios')
        ]);
        
        const trades = tradesResponse.trades || [];
        const portfolios = portfoliosResponse.portfolios || [];
        
        createTradingVolumeChart(trades);
        createPortfolioYieldChart(portfolios);
        
    } catch (error) {
        console.error('Error loading trading charts:', error);
    }
}

// Create trading volume chart
function createTradingVolumeChart(trades) {
    const ctx = document.getElementById('tradingVolumeChart');
    if (!ctx) return;
    
    // Group trades by date
    const dailyVolume = {};
    trades.forEach(trade => {
        const date = new Date(trade.trade_timestamp).toISOString().split('T')[0];
        dailyVolume[date] = (dailyVolume[date] || 0) + trade.trade_price;
    });
    
    const sortedDates = Object.keys(dailyVolume).sort();
    const volumes = sortedDates.map(date => dailyVolume[date]);
    
    if (tradingCharts.volume) {
        tradingCharts.volume.destroy();
    }
    
    tradingCharts.volume = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sortedDates,
            datasets: [{
                label: 'Trading Volume ($)',
                data: volumes,
                backgroundColor: '#3b82f6',
                borderColor: '#60a5fa',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#9ca3af' }
                },
                tooltip: {
                    callbacks: {
                        label: (context) => `Volume: ${formatCurrency(context.parsed.y)}`
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: '#374151' },
                    ticks: { 
                        color: '#9ca3af',
                        callback: (value) => formatCurrency(value)
                    }
                },
                x: {
                    grid: { color: '#374151' },
                    ticks: { color: '#9ca3af' }
                }
            }
        }
    });
}

// Create portfolio yield chart
function createPortfolioYieldChart(portfolios) {
    const ctx = document.getElementById('portfolioYieldChart');
    if (!ctx) return;
    
    const yields = portfolios.map(p => p.portfolio_yield * 100);
    
    const bins = [0, 2, 4, 6, 8, 10];
    const counts = new Array(bins.length - 1).fill(0);
    
    yields.forEach(yieldVal => {
        for (let i = 0; i < bins.length - 1; i++) {
            if (yieldVal >= bins[i] && yieldVal < bins[i + 1]) {
                counts[i]++;
                break;
            }
        }
    });
    
    if (tradingCharts.yield) {
        tradingCharts.yield.destroy();
    }
    
    tradingCharts.yield = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['0-2%', '2-4%', '4-6%', '6-8%', '8-10%'],
            datasets: [{
                label: 'Portfolio Count',
                data: counts,
                backgroundColor: '#10b981',
                borderColor: '#34d399',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#9ca3af' }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: '#374151' },
                    ticks: { color: '#9ca3af' }
                },
                x: {
                    grid: { color: '#374151' },
                    ticks: { color: '#9ca3af' }
                }
            }
        }
    });
}

// Add portfolio card styling
const portfolioStyle = document.createElement('style');
portfolioStyle.textContent = `
    .portfolio-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid var(--border-color);
    }
    
    .portfolio-header h4 {
        margin: 0;
        color: var(--accent-color);
        font-size: 1.1rem;
    }
    
    .portfolio-details {
        margin-bottom: 1rem;
    }
    
    .detail-row {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px solid var(--border-color);
    }
    
    .detail-row:last-child {
        border-bottom: none;
    }
    
    .detail-row .label {
        color: var(--text-secondary);
        font-size: 0.9rem;
    }
    
    .detail-row .value {
        color: var(--text-primary);
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .portfolio-actions {
        display: flex;
        gap: 0.5rem;
    }
`;
document.head.appendChild(portfolioStyle);