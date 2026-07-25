const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const statusText = document.getElementById('statusText');
const statusIndicator = document.getElementById('statusIndicator');
const statusLabel = document.getElementById('statusLabel');
const msgCountEl = document.getElementById('msgCount');
const tokenCountEl = document.getElementById('tokenCount');
const sessionTimeEl = document.getElementById('sessionTime');

let messageCount = 0;
let totalChars = 0;
let currentMode = 'pentest';
let isStreaming = false;
let sessionStart = Date.now();

// Session timer
setInterval(() => {
    const elapsed = Math.floor((Date.now() - sessionStart) / 1000);
    const h = String(Math.floor(elapsed / 3600)).padStart(2, '0');
    const m = String(Math.floor((elapsed % 3600) / 60)).padStart(2, '0');
    const s = String(elapsed % 60).padStart(2, '0');
    sessionTimeEl.textContent = `${h}:${m}:${s}`;
}, 1000);

// Fake system stats (real stats would need a backend endpoint)
setInterval(() => {
    const cpu = 15 + Math.random() * 30;
    const ram = 40 + Math.random() * 20;
    const gpu = 5 + Math.random() * 15;
    document.getElementById('cpuBar').style.width = cpu + '%';
    document.getElementById('ramBar').style.width = ram + '%';
    document.getElementById('gpuBar').style.width = gpu + '%';
}, 2000);

function setMode(mode) {
    currentMode = mode;
    document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');

    const modePrompts = {
        pentest: 'Modo Pentest activado. Enfocare mis respuestas en seguridad ofensiva, vulnerabilidades y tecnicas de explotacion.',
        philosophy: 'Modo Filosofia activado. Podemos debatir sobre existencialismo, etica, logica y el sentido de la vida.',
        code: 'Modo Codigo activado. Te ayudo con programacion, algoritmos, arquitectura de software y debugging.',
        general: 'Modo General activado. Puedo ayudarte con cualquier tema.'
    };

    addMessage('system', modePrompts[mode]);
}

function addMessage(role, content) {
    const welcome = document.querySelector('.welcome-message');
    if (welcome) welcome.remove();

    const div = document.createElement('div');
    div.className = `message ${role}`;

    const time = new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
    const roleLabel = role === 'user' ? 'YOU' : role === 'assistant' ? 'NOVA' : 'SYSTEM';

    div.innerHTML = `
        <div class="message-bubble">${escapeHtml(content).replace(/\n/g, '<br>')}</div>
        <div class="message-meta">${roleLabel} | ${time}</div>
    `;

    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return div;
}

function addTypingIndicator() {
    const div = document.createElement('div');
    div.className = 'message assistant';
    div.id = 'typingIndicator';
    div.innerHTML = `
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return div;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function updateStats() {
    msgCountEl.textContent = messageCount;
    tokenCountEl.textContent = '~' + Math.floor(totalChars / 4);
}

function setStatus(text, color) {
    statusText.textContent = text;
    statusLabel.textContent = text;
    statusIndicator.style.background = color;
    statusIndicator.style.boxShadow = `0 0 8px ${color}`;
    statusLabel.style.color = color;
}

async function sendMessage() {
    const message = userInput.value.trim();
    if (!message || isStreaming) return;

    isStreaming = true;
    sendBtn.disabled = true;
    userInput.value = '';
    userInput.style.height = 'auto';

    messageCount++;
    totalChars += message.length;
    updateStats();

    addMessage('user', message);
    setStatus('THINKING', '#eab308');

    const typingDiv = addTypingIndicator();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        let fullResponse = '';
        let responseDiv = null;

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            for (const line of lines) {
                if (!line.startsWith('data: ')) continue;
                try {
                    const data = JSON.parse(line.slice(6));

                    if (data.content) {
                        if (!responseDiv) {
                            typingDiv.remove();
                            responseDiv = addMessage('assistant', '');
                            responseDiv.querySelector('.message-bubble').textContent = '';
                        }
                        fullResponse += data.content;
                        responseDiv.querySelector('.message-bubble').textContent = fullResponse;
                        chatMessages.scrollTop = chatMessages.scrollHeight;
                    }

                    if (data.done) {
                        totalChars += fullResponse.length;
                        updateStats();
                    }
                } catch (e) {}
            }
        }

        if (!responseDiv) {
            typingDiv.remove();
            addMessage('assistant', '[No response received]');
        }

    } catch (error) {
        typingDiv.remove();
        addMessage('system', `Error: ${error.message}`);
    }

    setStatus('ONLINE', '#22c55e');
    isStreaming = false;
    sendBtn.disabled = false;
    userInput.focus();
}

function sendQuick(text) {
    userInput.value = text;
    sendMessage();
}

function clearChat() {
    if (!confirm('Clear all conversation history?')) return;
    fetch('/api/clear', { method: 'POST' });
    chatMessages.innerHTML = '';
    messageCount = 0;
    totalChars = 0;
    updateStats();

    // Re-add welcome
    chatMessages.innerHTML = `
        <div class="welcome-message">
            <div class="welcome-icon">&#x2726;</div>
            <h2>NOVA ONLINE</h2>
            <p>Historial limpio. Estoy lista para una nueva conversacion.</p>
            <div class="quick-actions">
                <button onclick="sendQuick('Que es XSS y como funciona?')">XSS</button>
                <button onclick="sendQuick('Explicame el estoicismo')">Filosofia</button>
                <button onclick="sendQuick('Hazme un brainstorm de ideas')">Ideas</button>
                <button onclick="sendQuick('Que tecnologias debo aprender para pentesting?')">Roadmap</button>
            </div>
        </div>
    `;
}

function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
}

// Auto-resize textarea
userInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 120) + 'px';
});

// Focus on load
window.addEventListener('load', () => {
    userInput.focus();
    setStatus('ONLINE', '#22c55e');
});

// Load history on start
fetch('/api/history').then(r => r.json()).then(history => {
    if (history.length > 0) {
        document.querySelector('.welcome-message')?.remove();
        history.forEach(msg => {
            addMessage(msg.role, msg.content);
            messageCount++;
            totalChars += msg.content.length;
        });
        updateStats();
    }
});
