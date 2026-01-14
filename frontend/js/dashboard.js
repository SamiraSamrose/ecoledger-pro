let dashboardCharts = {};

// Load dashboard data and update metrics
async function loadDashboardData() {
    try {
        const data = await apiRequest('/analytics/dashboard');
        
        // Update metric cards
        updateMetricCard('totalLoans', data.total_loans, '+12%');
        updateMetricCard('approvalRate', formatPercentage(data.approval_rate), '+5%');
        updateMetricCard('totalValue', formatCurrency(data.total_loan_value), '+18%');
        updateMetricCard('avgESG', formatNumber(data.avg_esg_score, 1), '+3%');
        updateMetricCard('activePortfolios', data.total_portfolios, `+${data.total_portfolios}`);
        updateMetricCard('tradingVolume', formatCurrency(data.total_trading_volume), '+25%');
        updateMetricCard('complianceRate', formatPercentage(data.compliance_rate), '+2%');
        updateMetricCard('borrowerSavings', formatCurrency(data.total_borrower_savings), '+15%');
        
        // Load charts
        await loadDashboardCharts(data);
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showNotification('Error loading dashboard data', 'error');
    }
}

// Update metric card
function updateMetricCard(id, value, change) {
    const valueElement = document.getElementById(id);
    const changeElement = document.getElementById(id + 'Change');
    
    if (valueElement) {
        valueElement.textContent = value;
        valueElement.classList.add('flash-green');
        setTimeout(() => valueElement.classList.remove('flash-green'), 500);
    }
    
    if (changeElement && change) {
        changeElement.textContent = change;
    }
}

// Load dashboard charts
async function loadDashboardCharts(data) {
    try {
        // Load loan applications for charts
        const loansResponse = await apiRequest('/loans?limit=1000');
        const loans = loansResponse.applications || [];
        
        // Loan Trend Chart
        createLoanTrendChart(loans);
        
        // ESG Distribution Chart
        createESGDistributionChart(loans);
        
        // Portfolio Performance Chart
        const portfoliosResponse = await apiRequest('/portfolios');
        createPortfolioPerformanceChart(portfoliosResponse.portfolios || []);
        
        // Carbon Impact Chart
        createCarbonImpactChart(loans);
        
    } catch (error) {
        console.error('Error loading dashboard charts:', error);
    }
}

// Create loan trend chart
function createLoanTrendChart(loans) {
    const ctx = document.getElementById('loanTrendChart');
    if (!ctx) return;
    
    // Group loans by month
    const monthlyData = {};
    loans.forEach(loan => {
        const date = new Date(loan.application_date);
        const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
        monthlyData[monthKey] = (monthlyData[monthKey] || 0) + 1;
    });
    
    const sortedMonths = Object.keys(monthlyData).sort();
    const counts = sortedMonths.map(month => monthlyData[month]);
    
    if (dashboardCharts.loanTrend) {
        dashboardCharts.loanTrend.destroy();
    }
    
    dashboardCharts.loanTrend = new Chart(ctx, {
        type: 'line',
        data: {
            labels: sortedMonths,
            datasets: [{
                label: 'Loan Applications',
                data: counts,
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                tension: 0.4,
                fill: true
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

// Create ESG distribution chart
function createESGDistributionChart(loans) {
    const ctx = document.getElementById('esgDistributionChart');
    if (!ctx) return;
    
    const esgScores = loans.map(l => l.combined_credit_score || 0).filter(s => s > 0);
    
    const bins = [0, 20, 40, 60, 80, 100];
    const counts = new Array(bins.length - 1).fill(0);
    
    esgScores.forEach(score => {
        for (let i = 0; i < bins.length - 1; i++) {
            if (score >= bins[i] && score < bins[i + 1]) {
                counts[i]++;
                break;
            }
        }
    });
    
    if (dashboardCharts.esgDistribution) {
        dashboardCharts.esgDistribution.destroy();
    }
    
    dashboardCharts.esgDistribution = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['0-20', '20-40', '40-60', '60-80', '80-100'],
            datasets: [{
                label: 'Number of Loans',
                data: counts,
                backgroundColor: [
                    '#ef4444',
                    '#f59e0b',
                    '#eab308',
                    '#84cc16',
                    '#10b981'
                ]
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

// Create portfolio performance chart
function createPortfolioPerformanceChart(portfolios) {
    const ctx = document.getElementById('portfolioPerformanceChart');
    if (!ctx) return;
    
    const yields = portfolios.map(p => (p.portfolio_yield * 100).toFixed(2));
    const esgScores = portfolios.map(p => p.weighted_esg_score.toFixed(1));
    const labels = portfolios.map((p, i) => `P${i + 1}`);
    
    if (dashboardCharts.portfolioPerformance) {
        dashboardCharts.portfolioPerformance.destroy();
    }
    
    dashboardCharts.portfolioPerformance = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Portfolios',
                data: portfolios.map((p, i) => ({
                    x: p.weighted_esg_score,
                    y: p.portfolio_yield * 100
                })),
                backgroundColor: '#3b82f6',
                borderColor: '#60a5fa',
                pointRadius: 6
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
                        label: (context) => {
                            return `ESG: ${context.parsed.x.toFixed(1)}, Yield: ${context.parsed.y.toFixed(2)}%`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    title: {
                        display: true,
                        text: 'Portfolio Yield (%)',
                        color: '#9ca3af'
                    },
                    grid: { color: '#374151' },
                    ticks: { color: '#9ca3af' }
                },
                x: {
                    title: {
                        display: true,
                        text: 'ESG Score',
                        color: '#9ca3af'
                    },
                    grid: { color: '#374151' },
                    ticks: { color: '#9ca3af' }
                }
            }
        }
    });
}

// Create carbon impact chart
function createCarbonImpactChart(loans) {
    const ctx = document.getElementById('carbonImpactChart');
    if (!ctx) return;
    
    const projectTypes = {};
    loans.forEach(loan => {
        const type = loan.project_type || 'Unknown';
        if (!projectTypes[type]) {
            projectTypes[type] = { count: 0, totalCarbon: 0 };
        }
        projectTypes[type].count++;
        projectTypes[type].totalCarbon += (loan.combined_credit_score || 0);
    });
    
    const labels = Object.keys(projectTypes);
    const data = labels.map(label => projectTypes[label].totalCarbon / projectTypes[label].count);
    
    if (dashboardCharts.carbonImpact) {
        dashboardCharts.carbonImpact.destroy();
    }
    
    dashboardCharts.carbonImpact = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    '#10b981',
                    '#3b82f6',
                    '#f59e0b',
                    '#ef4444',
                    '#8b5cf6',
                    '#ec4899',
                    '#14b8a6',
                    '#f97316'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: { color: '#9ca3af' }
                }
            }
        }
    });
}