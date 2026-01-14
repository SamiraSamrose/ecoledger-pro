async function loadAnalyticsData() {
    try {
        const [loansResponse, portfoliosResponse, tradesResponse] = await Promise.all([
            apiRequest('/loans?limit=1000'),
            apiRequest('/portfolios'),
            apiRequest('/trades')
        ]);
        
        const loans = loansResponse.applications || [];
        const portfolios = portfoliosResponse.portfolios || [];
        const trades = tradesResponse.trades || [];
        
        createPerformancePlot(loans, portfolios, trades);
        createRiskDistributionChart(loans);
        createProjectTypeChart(loans);
        createScatterPlot(loans);
        createGeoDistributionChart(loans);
        
        showNotification('Analytics data loaded', 'success');
        
    } catch (error) {
        console.error('Error loading analytics data:', error);
        showNotification('Error loading analytics data', 'error');
    }
}

// Create performance plot using Plotly
function createPerformancePlot(loans, portfolios, trades) {
    const container = document.getElementById('performancePlot');
    if (!container) return;
    
    const approvedLoans = loans.filter(l => l.loan_approved);
    
    const trace1 = {
        x: approvedLoans.map((l, i) => i + 1),
        y: approvedLoans.map(l => l.combined_credit_score),
        mode: 'lines+markers',
        name: 'Credit Score',
        line: { color: '#10b981', width: 2 },
        marker: { size: 6 }
    };
    
    const trace2 = {
        x: approvedLoans.map((l, i) => i + 1),
        y: approvedLoans.map(l => l.esg_composite_score),
        mode: 'lines+markers',
        name: 'ESG Score',
        line: { color: '#3b82f6', width: 2 },
        marker: { size: 6 }
    };
    
    const trace3 = {
        x: approvedLoans.map((l, i) => i + 1),
        y: approvedLoans.map(l => l.financial_health_score),
        mode: 'lines+markers',
        name: 'Financial Health',
        line: { color: '#f59e0b', width: 2 },
        marker: { size: 6 }
    };
    
    const layout = {
        title: {
            text: 'Loan Performance Metrics Over Time',
            font: { color: '#f9fafb' }
        },
        paper_bgcolor: '#1a1f2e',
        plot_bgcolor: '#1a1f2e',
        xaxis: {
            title: 'Loan Number',
            gridcolor: '#374151',
            color: '#9ca3af'
        },
        yaxis: {
            title: 'Score',
            gridcolor: '#374151',
            color: '#9ca3af',
            range: [0, 100]
        },
        legend: {
            font: { color: '#9ca3af' }
        }
    };
    
    Plotly.newPlot(container, [trace1, trace2, trace3], layout, {responsive: true});
}

// Create risk distribution chart
function createRiskDistributionChart(loans) {
    const ctx = document.getElementById('riskDistributionChart');
    if (!ctx) return;
    
    const riskCategories = {
        'Low Risk': 0,
        'Medium Risk': 0,
        'High Risk': 0,
        'Very High Risk': 0
    };
    
    loans.forEach(loan => {
        const score = loan.combined_credit_score || 0;
        if (score >= 80) {
            riskCategories['Low Risk']++;
        } else if (score >= 60) {
            riskCategories['Medium Risk']++;
        } else if (score >= 40) {
            riskCategories['High Risk']++;
        } else {
            riskCategories['Very High Risk']++;
        }
    });
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: Object.keys(riskCategories),
            datasets: [{
                data: Object.values(riskCategories),
                backgroundColor: [
                    '#10b981',
                    '#f59e0b',
                    '#ef4444',
                    '#7f1d1d'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#9ca3af' }
                },
                tooltip: {
                    callbacks: {
                        label: (context) => {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return `${context.label}: ${context.parsed} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Create project type chart
function createProjectTypeChart(loans) {
    const ctx = document.getElementById('projectTypeChart');
    if (!ctx) return;
    
    const projectTypes = {};
    loans.forEach(loan => {
        const type = loan.project_type || 'Unknown';
        projectTypes[type] = (projectTypes[type] || 0) + 1;
    });
    
    const sortedTypes = Object.entries(projectTypes)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 8);
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sortedTypes.map(t => t[0]),
            datasets: [{
                label: 'Number of Projects',
                data: sortedTypes.map(t => t[1]),
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
            indexAxis: 'y',
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    grid: { color: '#374151' },
                    ticks: { color: '#9ca3af' }
                },
                y: {
                    grid: { color: '#374151' },
                    ticks: { color: '#9ca3af' }
                }
            }
        }
    });
}

// Create scatter plot using Plotly
function createScatterPlot(loans) {
    const container = document.getElementById('scatterPlot');
    if (!container) return;
    
    const approvedLoans = loans.filter(l => l.loan_approved && l.combined_credit_score && l.esg_composite_score);
    
    const trace = {
        x: approvedLoans.map(l => l.esg_composite_score),
        y: approvedLoans.map(l => l.combined_credit_score),
        mode: 'markers',
        type: 'scatter',
        marker: {
            size: approvedLoans.map(l => Math.sqrt(l.loan_amount) / 100),
            color: approvedLoans.map(l => l.financial_health_score),
            colorscale: 'Viridis',
            showscale: true,
            colorbar: {
                title: 'Financial Health',
                titlefont: { color: '#9ca3af' },
                tickfont: { color: '#9ca3af' }
            }
        },
        text: approvedLoans.map(l => `Loan: ${l.loan_id}<br>Amount: ${formatCurrency(l.loan_amount)}`),
        hovertemplate: '%{text}<br>ESG: %{x:.1f}<br>Credit: %{y:.1f}<extra></extra>'
    };
    
    const layout = {
        title: {
            text: 'Credit Score vs ESG Score (size=loan amount)',
            font: { color: '#f9fafb' }
        },
        paper_bgcolor: '#1a1f2e',
        plot_bgcolor: '#1a1f2e',
        xaxis: {
            title: 'ESG Composite Score',
            gridcolor: '#374151',
            color: '#9ca3af',
            range: [0, 100]
        },
        yaxis: {
            title: 'Combined Credit Score',
            gridcolor: '#374151',
            color: '#9ca3af',
            range: [0, 100]
        }
    };
    
    Plotly.newPlot(container, [trace], layout, {responsive: true});
}

// Create geographical distribution chart
function createGeoDistributionChart(loans) {
    const ctx = document.getElementById('geoDistributionChart');
    if (!ctx) return;
    
    const countries = {};
    loans.forEach(loan => {
        const country = loan.country || 'Unknown';
        countries[country] = (countries[country] || 0) + 1;
    });
    
    const sortedCountries = Object.entries(countries)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 15);
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sortedCountries.map(c => c[0]),
            datasets: [{
                label: 'Number of Loans',
                data: sortedCountries.map(c => c[1]),
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
                    ticks: { 
                        color: '#9ca3af',
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            }
        }
    });
}

// Document upload handler
async function handleDocumentUploadSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    
    submitButton.textContent = 'Processing...';
    submitButton.disabled = true;
    
    try {
        const formData = new FormData(form);
        
        const response = await fetch(`${API_BASE_URL}/documents/upload`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Upload failed');
        }
        
        showNotification('Document uploaded and processed successfully', 'success');
        form.reset();
        await loadDocumentsList();
        
    } catch (error) {
        console.error('Error uploading document:', error);
        showNotification(error.message || 'Error uploading document', 'error');
    } finally {
        submitButton.textContent = originalText;
        submitButton.disabled = false;
    }
}

// Load documents list
async function loadDocumentsList() {
    try {
        const response = await apiRequest('/documents');
        const documents = response.documents || [];
        
        const tbody = document.getElementById('documentsTableBody');
        if (!tbody) return;
        
        if (documents.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: var(--text-secondary);">No documents found</td></tr>';
            return;
        }
        
        tbody.innerHTML = documents.map(doc => `
            <tr>
                <td>${doc.document_id}</td>
                <td>${doc.loan_id}</td>
                <td>${doc.document_type}</td>
                <td>
                    <span class="status-badge ${doc.verification_status === 'Verified' ? 'status-verified' : 'status-pending'}">
                        ${doc.verification_status}
                    </span>
                </td>
                <td>${formatPercentage(doc.ocr_confidence * 100, 1)}</td>
                <td>${new Date(doc.upload_timestamp).toLocaleString()}</td>
                <td>
                    <button class="btn btn-secondary" style="padding: 0.25rem 0.75rem; font-size: 0.85rem;" 
                            onclick="viewDocument('${doc.document_id}')">
                        View
                    </button>
                </td>
            </tr>
        `).join('');
        
        // Create OCR confidence chart
        createOCRConfidenceChart(documents);
        
    } catch (error) {
        console.error('Error loading documents:', error);
    }
}

// View document details
async function viewDocument(documentId) {
    try {
        const doc = await apiRequest(`/documents/${documentId}`);
        
        const details = `
            <strong>Document ID:</strong> ${doc.document_id}<br>
            <strong>Loan ID:</strong> ${doc.loan_id}<br>
            <strong>Type:</strong> ${doc.document_type}<br>
            <strong>Status:</strong> ${doc.verification_status}<br>
            <strong>Confidence:</strong> ${formatPercentage(doc.ocr_confidence * 100, 1)}<br>
            <strong>Pages:</strong> ${doc.page_count}<br>
            <strong>Size:</strong> ${doc.file_size_kb} KB<br>
            <strong>Uploaded:</strong> ${new Date(doc.upload_timestamp).toLocaleString()}<br>
        `;
        
        alert(details);
        
    } catch (error) {
        console.error('Error viewing document:', error);
        showNotification('Error loading document details', 'error');
    }
}

// Create OCR confidence chart
function createOCRConfidenceChart(documents) {
    const ctx = document.getElementById('ocrConfidenceChart');
    if (!ctx) return;
    
    const confidences = documents.map(d => d.ocr_confidence * 100);
    
    const bins = [0, 60, 70, 80, 90, 100];
    const counts = new Array(bins.length - 1).fill(0);
    
    confidences.forEach(conf => {
        for (let i = 0; i < bins.length - 1; i++) {
            if (conf >= bins[i] && conf < bins[i + 1]) {
                counts[i]++;
                break;
            }
        }
    });
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['0-60%', '60-70%', '70-80%', '80-90%', '90-100%'],
            datasets: [{
                label: 'Document Count',
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

// Rate engine functions
async function calculateRateAdjustment() {
    const loanId = document.getElementById('rateLoanId').value;
    if (!loanId) {
        showNotification('Please enter a loan ID', 'error');
        return;
    }
    
    try {
        const result = await apiRequest(`/rates/calculate/${loanId}`, {
            method: 'POST'
        });
        
        displayRateResult(result);
        showNotification('Rate adjustment calculated', 'success');
        
    } catch (error) {
        console.error('Error calculating rate adjustment:', error);
        showNotification(error.message || 'Error calculating rate adjustment', 'error');
    }
}

// Display rate result
function displayRateResult(result) {
    const container = document.getElementById('rateResult');
    if (!container) return;
    
    const discountClass = result.total_discount > 0 ? 'success' : 'neutral';
    
    container.innerHTML = `
        <div class="rate-result-card">
            <div class="rate-header">
                <h3>Rate Adjustment for ${result.loan_id}</h3>
            </div>
            <div class="rate-body">
                <div class="rate-comparison">
                    <div class="rate-item">
                        <span class="rate-label">Base Rate:</span>
                        <span class="rate-value">${formatPercentage(result.base_rate, 2)}</span>
                    </div>
                    <div class="rate-arrow">→</div>
                    <div class="rate-item ${discountClass}">
                        <span class="rate-label">Adjusted Rate:</span>
                        <span class="rate-value">${formatPercentage(result.adjusted_rate, 2)}</span>
                    </div>
                </div>
                <div class="rate-details">
                    <div class="rate-detail">
                        <span>Milestone Tier:</span>
                        <span>${result.milestone_tier}</span>
                    </div>
                    <div class="rate-detail">
                        <span>Total Discount:</span>
                        <span class="success-text">${formatPercentage(result.total_discount, 2)}</span>
                    </div>
                    <div class="rate-detail">
                        <span>Rate Change:</span>
                        <span class="${result.rate_change_pct < 0 ? 'success-text' : 'error-text'}">
                            ${formatPercentage(result.rate_change_pct, 2)}
                        </span>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Load rate history
async function loadRateHistory() {
    const loanId = document.getElementById('rateLoanId').value;
    if (!loanId) {
        showNotification('Please enter a loan ID', 'error');
        return;
    }
    
    try {
        const response = await apiRequest(`/rates/history/${loanId}`);
        const history = response.history || [];
        
        if (history.length === 0) {
            showNotification('No rate history found', 'error');
            return;
        }
        
        createRateHistoryChart(history);
        await loadSavingsSummary(loanId);
        
        showNotification('Rate history loaded', 'success');
        
    } catch (error) {
        console.error('Error loading rate history:', error);
        showNotification(error.message || 'Error loading rate history', 'error');
    }
}

// Create rate history chart
function createRateHistoryChart(history) {
    const ctx = document.getElementById('rateHistoryChart');
    if (!ctx) return;
    
    const months = history.map(h => h.month);
    const baseRates = history.map(h => h.base_rate);
    const adjustedRates = history.map(h => h.adjusted_rate);
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: months,
            datasets: [{
                label: 'Base Rate',
                data: baseRates,
                borderColor: '#ef4444',
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                tension: 0.4
            }, {
                label: 'Adjusted Rate',
                data: adjustedRates,
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                tension: 0.4
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
                    ticks: { 
                        color: '#9ca3af',
                        callback: (value) => `${value}%`
                    }
                },
                x: {
                    grid: { color: '#374151' },
                    ticks: { color: '#9ca3af' }
                }
            }
        }
    });
    
    // Create milestone tiers chart
    const tiers = history.map(h => h.milestone_tier);
    const tierCounts = {};
    tiers.forEach(tier => {
        tierCounts[tier] = (tierCounts[tier] || 0) + 1;
    });
    
    const milestoneCTX = document.getElementById('milestoneTiersChart');
    if (milestoneCTX) {
        new Chart(milestoneCTX, {
            type: 'doughnut',
            data: {
                labels: Object.keys(tierCounts),
                datasets: [{
                    data: Object.values(tierCounts),
                    backgroundColor: [
                        '#ef4444',
                        '#f59e0b',
                        '#eab308',
                        '#10b981',
                        '#3b82f6',
                        '#8b5cf6'
                    ]
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
}

// Load savings summary
async function loadSavingsSummary(loanId) {
    try {
        const savings = await apiRequest(`/rates/savings/${loanId}`);
        
        const container = document.getElementById('savingsSummary');
        if (!container) return;
        
        container.innerHTML = `
            <h3>Borrower Savings Summary</h3>
            <div class="savings-grid">
                <div class="savings-metric">
                    <span class="label">Loan Amount:</span>
                    <span class="value">${formatCurrency(savings.loan_amount)}</span>
                </div>
                <div class="savings-metric">
                    <span class="label">Base Interest:</span>
                    <span class="value">${formatCurrency(savings.base_interest)}</span>
                </div>
                <div class="savings-metric">
                    <span class="label">Adjusted Interest:</span>
                    <span class="value">${formatCurrency(savings.adjusted_interest)}</span>
                </div>
                <div class="savings-metric highlight">
                    <span class="label">Total Savings:</span>
                    <span class="value success-text">${formatCurrency(savings.total_savings)}</span>
                </div>
                <div class="savings-metric highlight">
                    <span class="label">Savings Percentage:</span>
                    <span class="value success-text">${formatPercentage(savings.savings_pct, 1)}</span>
                </div>
            </div>
        `;
        
    } catch (error) {
        console.error('Error loading savings summary:', error);
    }
}

// Ledger functions
async function validateLedger() {
    try {
        const result = await apiRequest('/ledger/validate');
        
        const container = document.getElementById('ledgerStatus');
        if (!container) return;
        
        const statusClass = result.is_valid ? 'success' : 'error';
        
        container.innerHTML = `
            <div class="ledger-validation ${statusClass}">
                <h3>Blockchain Validation ${result.is_valid ? 'Successful' : 'Failed'}</h3>
                <p>${result.message}</p>
            </div>
        `;
        
        showNotification(result.message, result.is_valid ? 'success' : 'error');
        
    } catch (error) {
        console.error('Error validating ledger:', error);
        showNotification('Error validating ledger', 'error');
    }
}

// Refresh ledger data
async function refreshLedgerData() {
    try {
        const response = await apiRequest('/ledger/query');
        const blocks = response.blocks || [];
        
        const tbody = document.getElementById('ledgerTableBody');
        if (!tbody) return;
        
        if (blocks.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: var(--text-secondary);">No transactions found</td></tr>';
            return;
        }
        
        tbody.innerHTML = blocks.slice(0, 50).map(block => `
            <tr>
                <td>${block.block_number}</td>
                <td>${new Date(block.timestamp).toLocaleString()}</td>
                <td><span class="status-badge status-verified">${block.transaction_type}</span></td>
                <td>${block.transaction_id}</td>
                <td>${block.portfolio_id || '-'}</td>
                <td>${block.amount ? formatCurrency(block.amount) : '-'}</td>
                <td style="font-family: monospace; font-size: 0.75rem;">${block.block_hash.substring(0, 16)}...</td>
            </tr>
        `).join('');
        
        showNotification('Ledger data refreshed', 'success');
        
    } catch (error) {
        console.error('Error refreshing ledger:', error);
        showNotification('Error refreshing ledger data', 'error');
    }
}

// Add rate styling
const rateStyle = document.createElement('style');
rateStyle.textContent = `
    .rate-result-card {
        border: 1px solid var(--border-color);
        border-radius: 8px;
        overflow: hidden;
    }
    
    .rate-header {
        padding: 1.5rem;
        background-color: var(--secondary-bg);
        border-bottom: 1px solid var(--border-color);
    }
    
    .rate-header h3 {
        margin: 0;
        color: var(--accent-color);
    }
    
    .rate-body {
        padding: 1.5rem;
        background-color: var(--secondary-bg);
    }
    
    .rate-comparison {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 2rem;
        margin-bottom: 2rem;
        padding: 1.5rem;
        background-color: var(--tertiary-bg);
        border-radius: 4px;
    }
    
    .rate-item {
        text-align: center;
    }
    
    .rate-item.success {
        color: var(--success-color);
    }
    
    .rate-label {
        display: block;
        font-size: 0.9rem;
        color: var(--text-secondary);
        margin-bottom: 0.5rem;
    }
    
    .rate-value {
        display: block;
        font-size: 2rem;
        font-weight: 700;
    }
    
    .rate-arrow {
        font-size: 2rem;
        color: var(--accent-color);
    }
    
    .rate-details {
        display: grid;
        gap: 1rem;
    }
    
    .rate-detail {
        display: flex;
        justify-content: space-between;
        padding: 0.75rem;
        background-color: var(--tertiary-bg);
        border-radius: 4px;
    }
    
    .savings-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
    }
    
    .savings-metric {
        display: flex;
        flex-direction: column;
        padding: 1rem;
        background-color: var(--tertiary-bg);
        border-radius: 4px;
    }
    
    .savings-metric.highlight {
        border: 2px solid var(--accent-color);
    }
    
    .savings-metric .label {
        color: var(--text-secondary);
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    
    .savings-metric .value {
        color: var(--text-primary);
        font-size: 1.5rem;
        font-weight: 700;
    }
    
    .ledger-validation {
        padding: 1.5rem;
        border-radius: 4px;
    }
    
    .ledger-validation.success {
        background-color: rgba(16, 185, 129, 0.1);
        border: 1px solid var(--success-color);
    }
    
    .ledger-validation.error {
        background-color: rgba(239, 68, 68, 0.1);
        border: 1px solid var(--error-color);
    }
    
    .ledger-validation h3 {
        margin: 0 0 0.5rem 0;
    }
    
    .ledger-validation p {
        margin: 0;
        color: var(--text-secondary);
    }
`;
document.head.appendChild(rateStyle);