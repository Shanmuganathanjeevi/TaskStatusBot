/**
 * Task Status Bot - Frontend Logic
 */

let isWaiting = false;

const questionInput = document.getElementById('questionInput');
const sendBtn = document.getElementById('sendBtn');
const chatMessages = document.getElementById('chatMessages');

function addMessageToChat(text, type = 'ai') {
    const now = new Date();
    const time = now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    
    let html;
    if (type === 'user') {
        html = `
            <div class="message user-message">
                <div class="message-content">${escapeHtml(text)}</div>
                <div class="message-time">${time}</div>
            </div>
        `;
    } else if (type === 'ai') {
        html = `
            <div class="message ai-message">
                <div class="message-content">${escapeHtml(text)}</div>
            </div>
        `;
    } else {
        html = `
            <div class="message ai-message">
                <div class="message-content" style="color: #dc2626;">${escapeHtml(text)}</div>
            </div>
        `;
    }
    
    chatMessages.innerHTML += html;
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addInitialGreeting() {
    addMessageToChat(
        "Hi there! 👋 I'm Shanmuganathan's Task Status Assistant. I can help you find information about tasks, deadlines, and blockers. What's your name?",
        'ai'
    );
}

async function askQuestion() {
    const question = questionInput.value.trim();
    if (!question) return;
    if (isWaiting) return;
    
    addMessageToChat(question, 'user');
    questionInput.value = '';
    questionInput.focus();
    
    isWaiting = true;
    sendBtn.disabled = true;
    questionInput.disabled = true;
    
    // Show typing indicator
    const typingId = addTypingIndicator();
    
    try {
        const response = await fetch('/api/answer', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({question})
        });
        
        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator(typingId);
        
        if (response.ok) {
            addMessageToChat(data.answer, 'ai');
            // If user is exiting, disable input
            if (data.is_exit) {
                questionInput.disabled = true;
                sendBtn.disabled = true;
                questionInput.placeholder = "Thanks for visiting!";
            }
        } else {
            throw new Error(data.message || 'Error');
        }
    } catch (error) {
        removeTypingIndicator(typingId);
        addMessageToChat(`❌ ${error.message}`, 'error');
    } finally {
        isWaiting = false;
        sendBtn.disabled = false;
        questionInput.disabled = false;
        questionInput.focus();
    }
}

function escapeHtml(text) {
    const map = {'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":"&#039;"};
    return text.replace(/[&<>"']/g, m => map[m]);
}

function addTypingIndicator() {
    // Show typing indicator while bot thinks
    const typingId = 'typing_' + Date.now();
    
    const html = `
        <div class="message ai-message" id="${typingId}">
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
            <div style="font-size: 0.85rem; color: #999; margin-top: 0.5rem;">Bot is thinking...</div>
        </div>
    `;
    
    chatMessages.innerHTML += html;
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return typingId;
}

function removeTypingIndicator(typingId) {
    // Remove typing indicator when response arrives
    const element = document.getElementById(typingId);
    if (element) {
        element.remove();
    }
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('📋 Task Status Bot loaded');
    
    // Show initial greeting from bot
    addInitialGreeting();
    
    questionInput.focus();
});

