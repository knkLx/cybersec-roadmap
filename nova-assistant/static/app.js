const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const statusText = document.getElementById('statusText');
const statusIndicator = document.getElementById('statusIndicator');
const statusLabel = document.getElementById('statusLabel');
const msgCountEl = document.getElementById('msgCount');
const tokenCountEl = document.getElementById('tokenCount');
const sessionTimeEl = document.getElementById('sessionTime');
const voiceBtn = document.getElementById('voiceBtn');
const voiceStatus = document.getElementById('voiceStatus');

let messageCount = 0;
let totalChars = 0;
let isStreaming = false;
let sessionStart = Date.now();

// Voice Recognition
let recognition = null;
let isListening = false;
let voiceEnabled = false;

if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'es-ES';

    recognition.onresult = (event) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript;
        }
        userInput.value = transcript;
        userInput.style.height = 'auto';
        userInput.style.height = Math.min(userInput.scrollHeight, 120) + 'px';

        if (event.results[event.results.length - 1].isFinal) {
            stopListening();
            setTimeout(() => sendMessage(), 300);
        }
    };

    recognition.onerror = (event) => {
        console.log('Speech error:', event.error);
        stopListening();
    };

    recognition.onend = () => {
        stopListening();
    };
}

function toggleVoice() {
    if (!recognition) {
        addMessage('system', 'Tu navegador no soporta reconocimiento de voz. Usa Chrome.');
        return;
    }
    if (isListening) {
        stopListening();
    } else {
        startListening();
    }
}

function startListening() {
    if (!recognition) return;
    isListening = true;
    voiceEnabled = true;
    voiceBtn.classList.add('listening');
    voiceStatus.textContent = 'Listening...';
    voiceStatus.style.color = '#ef4444';
    recognition.start();
}

function stopListening() {
    isListening = false;
    voiceBtn.classList.remove('listening');
    voiceStatus.textContent = voiceEnabled ? 'Voice ON' : 'Voice OFF';
    voiceStatus.style.color = voiceEnabled ? '#22c55e' : '';
    if (recognition && isListening) {
        recognition.stop();
    }
}

// Text-to-Speech for responses
function speak(text) {
    if (!voiceEnabled || !('speechSynthesis' in window)) return;

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'es-ES';
    utterance.rate = 1.0;
    utterance.pitch = 1.1;

    const voices = window.speechSynthesis.getVoices();
    const femaleVoice = voices.find(v => v.lang.startsWith('es') && v.name.toLowerCase().includes('female'))
        || voices.find(v => v.lang.startsWith('es'))
        || voices[0];
    if (femaleVoice) utterance.voice = femaleVoice;

    window.speechSynthesis.speak(utterance);
}

// Session timer
setInterval(() => {
    const elapsed = Math.floor((Date.now() - sessionStart) / 1000);
    const h = String(Math.floor(elapsed / 3600)).padStart(2, '0');
    const m = String(Math.floor((elapsed % 3600) / 60)).padStart(2, '0');
    const s = String(elapsed % 60).padStart(2, '0');
    sessionTimeEl.textContent = `${h}:${m}:${s}`;
}, 1000);

// Fake system stats
setInterval(() => {
    document.getElementById('cpuBar').style.width = (15 + Math.random() * 30) + '%';
    document.getElementById('ramBar').style.width = (40 + Math.random() * 20) + '%';
    document.getElementById('gpuBar').style.width = (5 + Math.random() * 15) + '%';
}, 2000);

function setMode(mode, btn) {
    document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
    if (btn) btn.classList.add('active');

    const prompts = {
        pentest: 'Modo Pentest. Enfocare en seguridad ofensiva y vulnerabilidades.',
        philosophy: 'Modo Filosofia. Puedo debatir sobre existencialismo, etica y logica.',
        code: 'Modo Codigo. Te ayudo con programacion y arquitectura.',
        general: 'Modo General. Puedo ayudarte con cualquier tema.'
    };
    addMessage('system', prompts[mode]);
}

function addMessage(role, content) {
    const welcome = document.querySelector('.welcome-message');
    if (welcome) welcome.remove();

    const div = document.createElement('div');
    div.className = `message ${role}`;
    const time = new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
    const label = role === 'user' ? 'YOU' : role === 'assistant' ? 'NOVA' : 'SYSTEM';
    div.innerHTML = `
        <div class="message-bubble">${escapeHtml(content).replace(/\n/g, '<br>')}</div>
        <div class="message-meta">${label} | ${time}</div>
    `;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return div;
}

function addTypingIndicator() {
    const div = document.createElement('div');
    div.className = 'message assistant';
    div.id = 'typingIndicator';
    div.innerHTML = `<div class="typing-indicator"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div>`;
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
                        // Speak the response
                        if (voiceEnabled && fullResponse.length < 500) {
                            speak(fullResponse);
                        }
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
    chatMessages.innerHTML = `
        <div class="welcome-message">
            <div class="welcome-icon">&#x2726;</div>
            <h2>NOVA ONLINE</h2>
            <p>Historial limpio. Estoy lista.</p>
            <div class="quick-actions">
                <button onclick="sendQuick('Que es XSS y como funciona?')">XSS</button>
                <button onclick="sendQuick('Explicame el estoicismo')">Filosofia</button>
                <button onclick="sendQuick('Hazme un brainstorm de ideas')">Ideas</button>
                <button onclick="sendQuick('Que tecnologias debo aprender para pentesting?')">Roadmap</button>
            </div>
        </div>
    `;
    messageCount = 0;
    totalChars = 0;
    updateStats();
}

// Key handler
userInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Auto-resize textarea
userInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 120) + 'px';
});

// Load voices for TTS
if ('speechSynthesis' in window) {
    window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
}

// Focus on load and load history
window.addEventListener('load', () => {
    userInput.focus();
    setStatus('ONLINE', '#22c55e');

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
});
