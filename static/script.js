const chatBox = document.getElementById('chatBox');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const hwStatusBadge = document.getElementById('hw-status');

// 1. Funzione per verificare lo stato dell'hardware dal backend
async function checkHardwareStatus() {
    try {
        const response = await fetch('/api/status');
        if (!response.ok) throw new Error('Network response was not ok');
        
        const data = await response.json();
        
        // Aggiorniamo sempre il badge indicando se si usa GPU o CPU
        if (data.cuda_active) {
            hwStatusBadge.textContent = 'CUDA GPU';
            hwStatusBadge.className = 'status status-gpu';
        } else {
            hwStatusBadge.textContent = 'CPU';
            hwStatusBadge.className = 'status status-cpu';
        }
        hwStatusBadge.style.display = 'inline-block';
    } catch (error) {
        console.error("Impossibile recuperare lo stato dell'hardware:", error);
    }
}

// Eseguiamo il controllo hardware all'avvio
checkHardwareStatus();


// 2. Funzioni di Chat
function appendMessage(sender, text) {
    const wrapperDiv = document.createElement('div');
    wrapperDiv.classList.add('message-wrapper', sender === 'user' ? 'user-wrapper' : 'bot-wrapper');

    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender === 'user' ? 'user-message' : 'bot-message');
    msgDiv.textContent = text;

    wrapperDiv.appendChild(msgDiv);
    chatBox.appendChild(wrapperDiv);
    scrollToBottom();
    return msgDiv;
}

function scrollToBottom() {
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    appendMessage('user', text);
    userInput.value = '';
    userInput.style.height = 'auto';
    userInput.disabled = true;
    sendBtn.disabled = true;

    const wrapperDiv = document.createElement('div');
    wrapperDiv.classList.add('message-wrapper', 'bot-wrapper');
    const botMsgDiv = document.createElement('div');
    botMsgDiv.classList.add('message', 'bot-message');
    botMsgDiv.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';

    wrapperDiv.appendChild(botMsgDiv);
    chatBox.appendChild(wrapperDiv);
    scrollToBottom();

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });

        if (!response.ok) throw new Error('Network response was not ok');

        botMsgDiv.innerHTML = '';

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            
            let newlineIndex;
            while ((newlineIndex = buffer.indexOf('\n\n')) >= 0) {
                const line = buffer.slice(0, newlineIndex);
                buffer = buffer.slice(newlineIndex + 2);
                
                if (line.startsWith('data: ')) {
                    const dataStr = line.substring(6);
                    if (dataStr === '[DONE]') {
                        return; // Fine dello stream
                    }
                    try {
                        const data = JSON.parse(dataStr);
                        if (data.error) {
                            botMsgDiv.innerHTML += `<br><span style="color: #fca5a5;">Errore: ${data.error}</span>`;
                        } else if (data.chunk) {
                            botMsgDiv.appendChild(document.createTextNode(data.chunk));
                        }
                        scrollToBottom();
                    } catch (e) {
                        console.warn("Dati incompleti o errore JSON, attendo il prossimo chunk...", e);
                    }
                }
            }
        }
    } catch (error) {
        console.error('Error:', error);
        botMsgDiv.innerHTML = '<span style="color: #ff8a8a;">Errore di connessione al server locale.</span>';
    } finally {
        userInput.disabled = false;
        sendBtn.disabled = false;
        userInput.focus();
    }
}

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});