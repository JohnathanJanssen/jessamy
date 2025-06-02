from flask import Flask, render_template, request, jsonify
from TTS.api import TTS
import os

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')

# Load the TTS model
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", vocoder_path=None, progress_bar=False, gpu=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    data = request.get_json()
    user_input = data.get('user_input', '').strip()

    if not user_input:
        return jsonify({'response': 'Please enter a message.'})

    # Basic logic for response (you can enhance this)
    response_text = f"Jessamy heard: {user_input}"

    # Generate speech audio file
    audio_path = os.path.join("static", "response.wav")
    tts.tts_to_file(text=response_text, file_path=audio_path)

    return jsonify({'response': response_text, 'audio': '/' + audio_path})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
