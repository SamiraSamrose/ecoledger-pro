async function handleLoanApplicationSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    
    submitButton.textContent = 'Processing...';
    submitButton.disabled = true;
    
    try {
        const formData = new FormData(form);
        const loanData = {};
        
        formData.forEach((value, key) => {
            if (value) {
                const numValue = parseFloat(value);
                loanData[key] = isNaN(numValue) ? value : numValue;
            }
        });
        
        const result = await apiRequest('/loans/apply', {
            method: 'POST',
            body: JSON.stringify(loanData)
        });
        
        displayLoanResult(result);
        showNotification('Loan application submitted successfully', 'success');
        form.reset();
        
    } catch (error) {
        console.error('Error submitting loan application:', error);
        showNotification(error.message || 'Error submitting loan application', 'error');
    } finally {
        submitButton.textContent = originalText;
        submitButton.disabled = false;
    }
}

function displayLoanResult(result) {
    const container = document.getElementById('loanResultContainer');
    const resultDiv = document.getElementById('loanResult');
    
    if (!container || !resultDiv) return;
    
    const statusClass = result.approved ? 'success' : 'error';
    const statusText = result.approved ? 'APPROVED' : 'REJECTED';
    
    resultDiv.innerHTML = `
        <div class="result-card">
            <div class="result-header ${statusClass}">
                <h3>Application ${statusText}</h3>
                <p>Loan ID: ${result.loan_id}</p>
            </div>
            <div class="result-body">
                <div class="result-metrics">
                    <div class="result-metric">
                        <span class="label">Financial Health Score:</span>
                        <span class="value">${formatNumber(result.financial_health_score, 2)}</span>
                    </div>
                    <div class="result-metric">
                        <span class="label">ESG Composite Score:</span>
                        <span class="value">${formatNumber(result.esg_composite_score, 2)}</span>
                    </div>
                    <div class="result-metric">
                        <span class="label">Combined Credit Score:</span>
                        <span class="value">${formatNumber(result.combined_credit_score, 2)}</span>
                    </div>
                    <div class="result-metric">
                        <span class="label">Processing Status:</span>
                        <span class="value">${result.processing_status}</span>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    container.style.display = 'block';
    container.scrollIntoView({ behavior: 'smooth' });
}

// Add result card styling
const resultStyle = document.createElement('style');
resultStyle.textContent = `
    .result-card {
        border: 1px solid var(--border-color);
        border-radius: 8px;
        overflow: hidden;
    }
    
    .result-header {
        padding: 1.5rem;
        color: white;
    }
    
    .result-header.success {
        background-color: var(--success-color);
    }
    
    .result-header.error {
        background-color: var(--error-color);
    }
    
    .result-header h3 {
        margin: 0;
        font-size: 1.5rem;
    }
    
    .result-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    .result-body {
        padding: 1.5rem;
        background-color: var(--secondary-bg);
    }
    
    .result-metrics {
        display: grid;
        gap: 1rem;
    }
    
    .result-metric {
        display: flex;
        justify-content: space-between;
        padding: 0.75rem;
        background-color: var(--tertiary-bg);
        border-radius: 4px;
    }
    
    .result-metric .label {
        color: var(--text-secondary);
        font-weight: 500;
    }
    
    .result-metric .value {
        color: var(--text-primary);
        font-weight: 700;
    }
`;
document.head.appendChild(resultStyle);