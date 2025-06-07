from flask import Flask, render_template, request, jsonify, send_file
import os
from tts import generate_speech  # Make sure this file exists and works

app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    data = request.get_json()
    user_input = data.get('user_input', '')
    voice_mode = data.get('voice_mode', False)

    if not user_input:
        return jsonify({'reply': 'Please enter a message.'})

    # Placeholder logic for Jessamy’s response
    reply_text = f"Jessamy heard: {user_input}"

    if voice_mode:
        generate_speech(reply_text)  # writes to static/output.wav
        return jsonify({'reply': reply_text, 'audio_url': '/static/output.wav'})
    else:
        return jsonify({'reply': reply_text})

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_file(os.path.join(app.static_folder, filename))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
