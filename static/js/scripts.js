document.addEventListener("DOMContentLoaded", function () {
  const sendButton = document.getElementById("send-button");
  const userInput = document.getElementById("user-input");
  const chatWindow = document.getElementById("chat-window");
  const voiceToggle = document.getElementById("voice-toggle");

  let voiceMode = false;

  // Toggle voice mode
  voiceToggle.addEventListener("click", function () {
      voiceMode = !voiceMode;
      voiceToggle.classList.toggle("active", voiceMode);
      voiceToggle.textContent = voiceMode ? "🔊" : "🎤";
  });

  // Send message
  sendButton.addEventListener("click", sendMessage);
  userInput.addEventListener("keypress", function (e) {
      if (e.key === "Enter") sendMessage();
  });

  function sendMessage() {
      const message = userInput.value.trim();
      if (message === "") return;

      appendMessage("user", message);
      userInput.value = "";

      fetch("/get_response", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_input: message, voice_mode: voiceMode })
      })
      .then(response => response.json())
      .then(data => {
          appendMessage("jessamy", data.reply);
          if (voiceMode && data.voice_generated) {
              const audio = new Audio("/static/output.wav");
              audio.play();
          }
      })
      .catch(error => {
          appendMessage("jessamy", "Error: Unable to reach Jessamy.");
          console.error("Error:", error);
      });
  }

  function appendMessage(sender, text) {
      const bubble = document.createElement("div");
      bubble.className = `message ${sender}`;
      bubble.textContent = text;
      chatWindow.appendChild(bubble);
      chatWindow.scrollTop = chatWindow.scrollHeight;
  }
});
