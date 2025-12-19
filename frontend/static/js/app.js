// Chat-style User Interface JavaScript

const API_BASE = '/api';

// Elements
const chatContainer = document.getElementById('chatContainer');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const newChatBtn = document.getElementById('newChatBtn');

// Chat history
let chatHistory = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('Chat interface loaded');
    
    // Auto-resize textarea
    chatInput.addEventListener('input', autoResizeTextarea);
    
    // Send message on button click
    sendBtn.addEventListener('click', () => {
        console.log('Send button clicked');
        sendMessage();
    });
    
    // Send on Enter (but not Shift+Enter)
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            console.log('Enter pressed');
            sendMessage();
        }
    });
    
    // New chat button
    if (newChatBtn) {
        newChatBtn.addEventListener('click', startNewChat);
    }
    
    // Example query buttons
    document.querySelectorAll('.example-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            chatInput.value = btn.dataset.query;
            chatInput.focus();
            autoResizeTextarea();
        });
    });
    
    // Focus input
    chatInput.focus();
});

function autoResizeTextarea() {
    chatInput.style.height = 'auto';
    chatInput.style.height = Math.min(chatInput.scrollHeight, 200) + 'px';
}

function startNewChat() {
    if (!confirm('Start a new conversation? This will clear the current chat.')) {
        return;
    }
    
    chatHistory = [];
    chatContainer.innerHTML = `
        <div class="welcome-message">
            <div class="empty-icon">💬</div>
            <h3>Start a new conversation</h3>
            <p>Ask questions about your documents</p>
            
            <div class="example-queries-chat">
                <p class="example-label">Example questions:</p>
                <div class="example-buttons">
                    <button class="example-btn" data-query="What was the average Central European ethylene price in May 2024?">
                        📊 Ethylene prices
                    </button>
                    <button class="example-btn" data-query="Compare Russian ethylene production in Q1 2024 versus Q1 2025">
                        📈 Production comparison
                    </button>
                    <button class="example-btn" data-query="What were Czech crude imports in Jan-Mar 2025?">
                        🛢️ Import data
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Re-attach example button listeners
    document.querySelectorAll('.example-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            chatInput.value = btn.dataset.query;
            chatInput.focus();
            autoResizeTextarea();
        });
    });
    
    chatInput.value = '';
    chatInput.style.height = 'auto';
    chatInput.focus();
}

async function sendMessage() {
    const question = chatInput.value.trim();
    
    console.log('Sending message:', question);
    
    if (!question) {
        console.log('Empty question, ignoring');
        return;
    }
    
    // Hide welcome message if exists
    const welcomeMsg = chatContainer.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    // Add user message to chat
    addUserMessage(question);
    
    // Clear input and reset height
    chatInput.value = '';
    chatInput.style.height = 'auto';
    
    // Add loading message
    const loadingId = addLoadingMessage();
    
    // Disable send button and input
    sendBtn.disabled = true;
    chatInput.disabled = true;
    
    try {
        console.log('Calling API...');
        
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
        
        console.log('API response status:', response.status);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('API error:', errorText);
            throw new Error(`Query failed: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('API response data:', data);
        
        // Remove loading message
        removeLoadingMessage(loadingId);
        
        // Add assistant response
        addAssistantMessage(data);
        
        // Save to history
        chatHistory.push({
            question: question,
            answer: data.answer,
            sources: data.sources,
            timestamp: new Date()
        });
        
    } catch (error) {
        console.error('Error:', error);
        removeLoadingMessage(loadingId);
        addErrorMessage(`Failed to process query: ${error.message}`);
    } finally {
        sendBtn.disabled = false;
        chatInput.disabled = false;
        chatInput.focus();
    }
}

function addUserMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message user-message';
    messageDiv.innerHTML = `
        <div class="message-content">
            <div class="message-avatar user-avatar">👤</div>
            <div class="message-text">${escapeHtml(text)}</div>
        </div>
    `;
    
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

function addAssistantMessage(data) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message assistant-message';
    
    // Format answer with paragraphs
    const formattedAnswer = formatAnswer(data.answer);
    
    messageDiv.innerHTML = `
        <div class="message-content">
            <div class="message-avatar assistant-avatar">🤖</div>
            <div class="message-text">
                <div class="answer-text">${formattedAnswer}</div>
                ${data.sources && data.sources.length > 0 ? createSourcesHTML(data.sources) : ''}
                <div class="message-meta">
                    <small>⏱️ ${data.processing_time.toFixed(2)}s</small>
                </div>
            </div>
        </div>
    `;
    
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

function addLoadingMessage() {
    const loadingId = 'loading-' + Date.now();
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message assistant-message';
    messageDiv.id = loadingId;
    messageDiv.innerHTML = `
        <div class="message-content">
            <div class="message-avatar assistant-avatar">🤖</div>
            <div class="message-text">
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        </div>
    `;
    
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
    
    return loadingId;
}

function removeLoadingMessage(loadingId) {
    const loadingMsg = document.getElementById(loadingId);
    if (loadingMsg) {
        loadingMsg.remove();
    }
}

function addErrorMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message assistant-message error-message';
    messageDiv.innerHTML = `
        <div class="message-content">
            <div class="message-avatar assistant-avatar">⚠️</div>
            <div class="message-text">
                <div class="answer-text">${escapeHtml(text)}</div>
            </div>
        </div>
    `;
    
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

function createSourcesHTML(sources) {
    if (!sources || sources.length === 0) return '';
    
    let html = '<div class="sources-compact">';
    html += '<p class="sources-label">📚 Sources:</p>';
    html += '<div class="sources-list-compact">';
    
    sources.slice(0, 5).forEach((source, index) => {
        const icon = getSourceIcon(source.type);
        html += `
            <div class="source-tag" title="${escapeHtml(source.filename)}">
                ${icon} ${escapeHtml(source.filename)}
            </div>
        `;
    });
    
    html += '</div></div>';
    return html;
}

function formatAnswer(text) {
    if (!text) return '';
    
    // Convert line breaks to paragraphs
    const paragraphs = text.split('\n\n');
    let formatted = paragraphs.map(p => {
        p = p.trim();
        if (!p) return '';
        
        // Check if it's a list item
        if (p.match(/^\d+\./)) {
            return `<div class="list-item">${escapeHtml(p)}</div>`;
        }
        
        return `<p>${escapeHtml(p)}</p>`;
    }).join('');
    
    return formatted;
}

function getSourceIcon(type) {
    const icons = {
        'pdf': '📕',
        'word': '📄',
        'excel': '📊'
    };
    return icons[type] || '📄';
}

function scrollToBottom() {
    setTimeout(() => {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }, 100);
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}