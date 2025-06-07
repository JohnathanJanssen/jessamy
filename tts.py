import os
from TTS.api import TTS

# Load TTS model
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False, gpu=False)

def generate_speech(text: str, output_path="static/response.wav"):
    if not text:
        raise ValueError("No text provided for speech synthesis.")
    
    # Ensure static folder exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Generate speech
    tts.tts_to_file(text=text, file_path=output_path)
