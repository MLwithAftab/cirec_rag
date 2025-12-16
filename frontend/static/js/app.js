// User Interface JavaScript

const API_BASE = '/api';

// Elements
const queryInput = document.getElementById('queryInput');
const submitBtn = document.getElementById('submitQuery');
const resultsSection = document.getElementById('resultsSection');
const emptyState = document.getElementById('emptyState');
const answerContent = document.getElementById('answerContent');
const sourcesContent = document.getElementById('sourcesContent');
const processingTime = document.getElementById('processingTime');

// Example query buttons
document.querySelectorAll('.example-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        queryInput.value = btn.dataset.query;
        submitQuery();
    });
});

// Submit query
submitBtn.addEventListener('click', submitQuery);

// Enter key to submit (Ctrl+Enter)
queryInput.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
        submitQuery();
    }
});

async function submitQuery() {
    const question = queryInput.value.trim();
    
    if (!question) {
        alert('Please enter a question');
        return;
    }
    
    // Show loading state
    submitBtn.disabled = true;
    submitBtn.querySelector('.btn-text').style.display = 'none';
    submitBtn.querySelector('.btn-loading').style.display = 'inline-block';
    
    emptyState.style.display = 'none';
    resultsSection.style.display = 'none';
    
    try {
        const response = await fetch(`${API_BASE}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: question,
                top_k: 10
            })
        });
        
        if (!response.ok) {
            throw new Error('Query failed');
        }
        
        const data = await response.json();
        
        // Display results
        displayResults(data);
        
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to process query. Please try again.');
    } finally {
        // Reset button state
        submitBtn.disabled = false;
        submitBtn.querySelector('.btn-text').style.display = 'inline';
        submitBtn.querySelector('.btn-loading').style.display = 'none';
    }
}

function displayResults(data) {
    // Show results section
    resultsSection.style.display = 'block';
    
    // Display answer
    answerContent.textContent = data.answer;
    processingTime.textContent = data.processing_time.toFixed(2);
    
    // Display sources
    sourcesContent.innerHTML = '';
    
    if (data.sources && data.sources.length > 0) {
        data.sources.forEach((source, index) => {
            const sourceItem = createSourceElement(source, index + 1);
            sourcesContent.appendChild(sourceItem);
        });
    } else {
        sourcesContent.innerHTML = '<p style="color: var(--text-secondary);">No sources found</p>';
    }
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function createSourceElement(source, index) {
    const div = document.createElement('div');
    div.className = 'source-item';
    
    const icon = getSourceIcon(source.type);
    const typeLabel = source.type.toUpperCase();
    
    div.innerHTML = `
        <div class="source-icon">${icon}</div>
        <div class="source-info">
            <div>
                <span class="source-type">${typeLabel}</span>
                <span class="source-filename">${source.filename}</span>
            </div>
            ${source.content ? `<div class="source-content">${source.content}</div>` : ''}
        </div>
    `;
    
    return div;
}

function getSourceIcon(type) {
    const icons = {
        'pdf': '📕',
        'word': '📄',
        'excel': '📊'
    };
    return icons[type] || '📄';
}