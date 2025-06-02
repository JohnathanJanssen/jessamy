document.addEventListener('DOMContentLoaded', () => {
  const sendButton = document.getElementById('send-button');
  const inputField = document.getElementById('user-input');
  const chatWindow = document.getElementById('chat-window');
  const voiceToggle = document.getElementById('voice-toggle');
  let voiceMode = false;

  function appendMessage(text, sender) {
      const message = document.createElement('div');
      message.className = sender;
      message.textContent = text;
      chatWindow.appendChild(message);
      chatWindow.scrollTop = chatWindow.scrollHeight;
  }

  async function sendMessage() {
      const userInput = inputField.value.trim();
      if (!userInput) return;

      appendMessage(userInput, 'user');
      inputField.value = '';

      try {
          const response = await fetch('/get_response', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                  user_input: userInput,
                  voice_mode: voiceMode
              })
          });

          const data = await response.json();

          // Check and display Jessamy's reply
          if (data.reply) {
              appendMessage(data.reply, 'jessamy');
          } else {
              appendMessage("No reply received.", 'jessamy');
          }

      } catch (error) {
          console.error('Error fetching reply:', error);
          appendMessage('Error communicating with Jessamy.', 'jessamy');
      }
  }

  sendButton.addEventListener('click', sendMessage);
  inputField.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') sendMessage();
  });

  voiceToggle.addEventListener('click', () => {
      voiceMode = !voiceMode;
      voiceToggle.classList.toggle('active');
  });
});
