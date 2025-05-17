const chatWindow = document.getElementById('chat-window');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const voiceToggle = document.getElementById('voice-toggle');

let voiceMode = false;

// Setup Web Speech API
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition;
if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false; // important: still false, because we want one sentence then control when to restart
    recognition.lang = 'en-US';
    recognition.interimResults = false;

    recognition.onresult = function (event) {
        const transcript = event.results[0][0].transcript;
        userInput.value = transcript;
        sendMessage(); // Send message after speaking
    };

    recognition.onerror = function (event) {
        console.error('Speech recognition error:', event.error);
        // Restart if needed
        if (voiceMode) {
            recognition.stop();
            setTimeout(() => recognition.start(), 500);
        }
    };

    recognition.onend = function () {
        if (voiceMode) {
            // If voice mode is still active, restart recognition after short delay
            setTimeout(() => recognition.start(), 500);
        }
    };
} else {
    console.warn("Speech Recognition API not supported.");
}

voiceToggle.addEventListener('click', () => {
    voiceMode = !voiceMode;
    voiceToggle.style.backgroundColor = voiceMode ? '#c084fc' : '#7c3aed';

    if (voiceMode && recognition) {
        recognition.start();
    } else if (recognition) {
        recognition.stop();
    }
});

sendButton.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

function appendMessage(sender, message) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);
    messageDiv.innerText = message;
    chatWindow.appendChild(messageDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function sendMessage() {
    const message = userInput.value.trim();
    if (message === '') return;

    appendMessage('user', message);
    userInput.value = '';

    fetch('/get_response', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        appendMessage('jessamy', data.response);

        if (voiceMode) {
            speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(data.response.trim());
            utterance.rate = 1.0;
            speechSynthesis.speak(utterance);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
