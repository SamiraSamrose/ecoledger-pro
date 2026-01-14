let monitoringCharts = {};

// Load monitoring data for a loan
async function loadMonitoringData() {
    const loanId = document.getElementById('monitorLoanId').value;
    if (!loanId) {
        showNotification('Please enter a loan ID', 'error');
        return;
    }
    
    try {
        const [status, history, alerts] = await Promise.all([
            apiRequest(`/monitoring/status/${loanId}`),
            apiRequest(`/monitoring/history/${loanId}`),
            apiRequest('/monitoring/alerts')
        ]);
        
        displayMonitoringStatus(status);
        createMonitoringCharts(history);
        displayComplianceAlerts(alerts.alerts || []);
        
        showNotification('Monitoring data loaded', 'success');
        
    } catch (error) {
        console.error('Error loading monitoring data:', error);
        showNotification(error.message || 'Error loading monitoring data', 'error');
    }
}

// Generate test monitoring data
async function generateMonitoringData() {
    const loanId = document.getElementById('monitorLoanId').value;
    if (!loanId) {
        showNotification('Please enter a loan ID', 'error');
        return;
    }
    
    try {
        await apiRequest(`/monitoring/generate/${loanId}`, {
            method: 'POST',
            body: JSON.stringify({ months: 12 })
        });
        
        showNotification('Monitoring data generated', 'success');
        await loadMonitoringData();
        
    } catch (error) {
        console.error('Error generating monitoring data:', error);
        showNotification(error.message || 'Error generating monitoring data', 'error');
    }
}

// Display monitoring status
function displayMonitoringStatus(status) {
    const container = document.getElementById('monitoringStatus');
    if (!container || !status) return;
    
    const statusClass = status.in_compliance ? 'success' : 'error';
    
    container.innerHTML = `
        <div class="monitoring-status-card">
            <div class="status-header ${statusClass}">
                <h3>Loan ${status.loan_id}</h3>
                <span class="status-badge ${status.in_compliance ? 'status-verified' : 'status-failed'}">
                    ${status.project_status}
                </span>
            </div>
            <div class="status-body">
                <div class="status-metrics">
                    <div class="status-metric">
                        <span class="label">Energy Savings:</span>
                        <span class="value ${status.energy_savings_pct >= 10 ? 'success-text' : 'error-text'}">
                            ${formatPercentage(status.energy_savings_pct, 1)}
                        </span>
                    </div>
                    <div class="status-metric">
                        <span class="label">Carbon Reduction:</span>
                        <span class="value ${status.carbon_reduction_pct >= 5 ? 'success-text' : 'error-text'}">
                            ${formatPercentage(status.carbon_reduction_pct, 1)}
                        </span>
                    </div>
                    <div class="status-metric">
                        <span class="label">Renewable Energy:</span>
                        <span class="value ${status.renewable_energy_pct >= 15 ? 'success-text' : 'error-text'}">
                            ${formatPercentage(status.renewable_energy_pct, 1)}
                        </span>
                    </div>
                    <div class="status-metric">
                        <span class="label">ESG Score:</span>
                        <span class="value ${status.esg_score >= 50 ? 'success-text' : 'error-text'}">
                            ${formatNumber(status.esg_score, 1)}
                        </span>
                    </div>
                    <div class="status-metric">
                        <span class="label">Data Source:</span>
                        <span class="value">${status.data_source}</span>
                    </div>
                    <div class="status-metric">
                        <span class="label">Last Updated:</span>
                        <span class="value">${new Date(status.monitoring_date).toLocaleString()}</span>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Create monitoring charts
function createMonitoringCharts(history) {
    if (!history || history.length === 0) return;
    
    const months = history.map(h => h.month);
    
    createEnergySavingsChart(months, history);
    createCarbonReductionChart(months, history);
    createESGScoreChart(months, history);
    createComplianceStatusChart(months, history);
}

// Create energy savings chart
function createEnergySavingsChart(months, history) {
    const ctx = document.getElementById('energySavingsChart');
    if (!ctx) return;
    
    const data = history.map(h => h.energy_savings_pct);
    
    if (monitoringCharts.energySavings) {
        monitoringCharts.energySavings.destroy();
    }
    
    monitoringCharts.energySavings = new Chart(ctx, {
        type: 'line',
        data: {
            labels: months,
            datasets: [{
                label: 'Energy Savings %',
                data: data,
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                tension: 0.4,
                fill: true
            }, {
                label: 'Threshold (10%)',
                data: new Array(months.length).fill(10),
                borderColor: '#ef4444',
                borderDash: [5, 5],
                pointRadius: 0
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

// Create carbon reduction chart
function createCarbonReductionChart(months, history) {
    const ctx = document.getElementById('carbonReductionChart');
    if (!ctx) return;
    
    const data = history.map(h => h.carbon_reduction_pct);
    
    if (monitoringCharts.carbonReduction) {
        monitoringCharts.carbonReduction.destroy();
    }
    
    monitoringCharts.carbonReduction = new Chart(ctx, {
        type: 'line',
        data: {
            labels: months,
            datasets: [{
                label: 'Carbon Reduction %',
                data: data,
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                tension: 0.4,
                fill: true
            }, {
                label: 'Threshold (5%)',
                data: new Array(months.length).fill(5),
                borderColor: '#ef4444',
                borderDash: [5, 5],
                pointRadius: 0
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

// Create ESG score chart
function createESGScoreChart(months, history) {
    const ctx = document.getElementById('esgScoreChart');
    if (!ctx) return;
    
    const data = history.map(h => h.esg_score);
    
    if (monitoringCharts.esgScore) {
        monitoringCharts.esgScore.destroy();
    }
    
    monitoringCharts.esgScore = new Chart(ctx, {
        type: 'line',
        data: {
            labels: months,
            datasets: [{
                label: 'ESG Score',
                data: data,
                borderColor: '#f59e0b',
                backgroundColor: 'rgba(245, 158, 11, 0.1)',
                tension: 0.4,
                fill: true
            }, {
                label: 'Threshold (50)',
                data: new Array(months.length).fill(50),
                borderColor: '#ef4444',
                borderDash: [5, 5],
                pointRadius: 0
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
                    max: 100,
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

// Create compliance status chart
function createComplianceStatusChart(months, history) {
    const ctx = document.getElementById('complianceStatusChart');
    if (!ctx) return;
    
    const compliantCount = history.filter(h => h.in_compliance).length;
    const nonCompliantCount = history.length - compliantCount;
    
    if (monitoringCharts.complianceStatus) {
        monitoringCharts.complianceStatus.destroy();
    }
    
    monitoringCharts.complianceStatus = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Compliant', 'Non-Compliant'],
            datasets: [{
                data: [compliantCount, nonCompliantCount],
                backgroundColor: ['#10b981', '#ef4444']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#9ca3af' }
                }
            }
        }
    });
}

// Display compliance alerts
function displayComplianceAlerts(alerts) {
    const container = document.getElementById('complianceAlerts');
    if (!container) return;
    
    if (alerts.length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary);">No compliance alerts</p>';
        return;
    }
    
    container.innerHTML = alerts.map(alert => `
        <div class="alert-card ${alert.severity.toLowerCase()}">
            <div class="alert-header">
                <h4>Loan ${alert.loan_id}</h4>
                <span class="status-badge ${alert.severity === 'High' ? 'status-failed' : 'status-pending'}">
                    ${alert.severity}
                </span>
            </div>
            <div class="alert-body">
                <div class="alert-violations">
                    <strong>Violations:</strong>
                    <ul>
                        ${alert.violation_reasons.map(reason => `<li>${reason}</li>`).join('')}
                    </ul>
                </div>
                <div class="alert-action">
                    <strong>Recommended Action:</strong>
                    <p>${alert.recommended_action}</p>
                </div>
                <div class="alert-date">
                    ${new Date(alert.monitoring_date).toLocaleString()}
                </div>
            </div>
        </div>
    `).join('');
}

// Add monitoring styling
const monitoringStyle = document.createElement('style');
monitoringStyle.textContent = `
    .monitoring-status-card {
        border: 1px solid var(--border-color);
        border-radius: 8px;
        overflow: hidden;
    }
    
    .status-header {
        padding: 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: white;
    }
    
    .status-header.success {
        background-color: var(--success-color);
    }
    
    .status-header.error {
        background-color: var(--error-color);
    }
    
    .status-header h3 {
        margin: 0;
        font-size: 1.3rem;
    }
    
    .status-body {
        padding: 1.5rem;
        background-color: var(--secondary-bg);
    }
    
    .status-metrics {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
    }
    
    .status-metric {
        display: flex;
        justify-content: space-between;
        padding: 0.75rem;
        background-color: var(--tertiary-bg);
        border-radius: 4px;
    }
    
    .success-text {
        color: var(--success-color);
    }
    
    .error-text {
        color: var(--error-color);
    }
    
    .alert-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .alert-header h4 {
        margin: 0;
        color: var(--text-primary);
    }
    
    .alert-body {
        color: var(--text-secondary);
    }
    
    .alert-violations ul {
        margin: 0.5rem 0;
        padding-left: 1.5rem;
    }
    
    .alert-action {
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid var(--border-color);
    }
    
    .alert-date {
        margin-top: 0.5rem;
        font-size: 0.85rem;
        color: var(--text-secondary);
    }
`;
document.head.appendChild(monitoringStyle);