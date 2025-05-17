const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const chatMessages = document.getElementById('chat-messages');

// Correct WebSocket path
const ws = new WebSocket(`ws://${window.location.host}/`);

ws.onmessage = (event) => {
    const message = JSON.parse(event.data);

    if (message.role === "assistant" && message.type === "message" && message.content) {
        addMessage(message.content, "assistant");
    }
};

sendButton.addEventListener('click', sendMessage);
userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

function sendMessage() {
    const text = userInput.value.trim();
    if (text === "") return;

    addMessage(text, "user");

    if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ role: "user", type: "message", content: text }));
    }

    userInput.value = "";
}

function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);
    messageDiv.innerText = text;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
