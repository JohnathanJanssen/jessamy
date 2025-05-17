# jessamy_tts.py

from TTS.api import TTS
import os

# Initialize once
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")

def speak(text: str, output_path: str = "output.wav"):
    """
    Generate speech from text and save to output_path.
    """
    tts.tts_to_file(text=text, file_path=output_path)
    print(f"[Jessamy] Speech saved to {output_path}")

    # Auto-play on Mac after saving
    os.system(f"afplay {output_path}")
