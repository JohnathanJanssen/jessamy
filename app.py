# app.py

from flask import Flask, render_template, request, jsonify
import subprocess
import threading
import openai
import os
from dotenv import load_dotenv

# Local TTS
from jessamy_tts import speak

# === CONFIGURATION ===
load_dotenv()  # Load variables from .env file
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

# === FUNCTIONS ===

def ask_gpt(message):
    """
    Sends a message to ChatGPT and returns the reply.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are Jessamy, a friendly and highly capable AI assistant created to help Johnathan with tasks on his MacBook."},
            {"role": "user", "content": message}
        ],
        temperature=0.6,
        max_tokens=500
    )
    reply = response['choices'][0]['message']['content'].strip()
    return reply

def speak_async(text):
    """
    Run Jessamy's TTS speaking in a background thread so the server remains responsive.
    """
    threading.Thread(target=speak, args=(text,)).start()

# === ROUTES ===

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    data = request.get_json()
    message = data.get('message', '')

    if not message:
        return jsonify({'reply': "I'm sorry, I didn't catch that."})

    # Get GPT reply
    reply = ask_gpt(message)

    # Speak reply (locally using Jessamy voice)
    speak_async(reply)

    return jsonify({'reply': reply})

# === RUN APP ===

if __name__ == '__main__':
    app.run(debug=True, port=5001)
