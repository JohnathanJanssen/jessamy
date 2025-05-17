import asyncio
import websockets
import json
import threading
import sys
import os
from pynput import keyboard

# Use this environment variable to point to your server
SERVER_URL = os.environ.get("SERVER_URL", "ws://0.0.0.0:10101")

class Client:
    def __init__(self):
        self.ws = None
        self.listening = False
        self.typing = False
        self.loop = asyncio.get_event_loop()

    async def connect(self):
        async with websockets.connect(SERVER_URL) as websocket:
            self.ws = websocket
            await self.listen()

    async def listen(self):
        input_thread = threading.Thread(target=self.keyboard_listener)
        input_thread.start()

        while True:
            try:
                response = await self.ws.recv()
                data = json.loads(response)
                if "text" in data:
                    print("\n\nAssistant:", data["text"])
                    print("\n(Type your message and press Enter, or hold CTRL to speak.)")
            except websockets.ConnectionClosed:
                print("Connection closed")
                break

    def keyboard_listener(self):
        def on_press(key):
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                if not self.listening:
                    self.listening = True
                    asyncio.run_coroutine_threadsafe(self.send_voice_request(), self.loop)

        def on_release(key):
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.listening = False

        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()

        while True:
            user_input = input("\n(Type your message and press Enter, or hold CTRL to speak):\n> ")
            asyncio.run_coroutine_threadsafe(self.send_text_request(user_input), self.loop)

    async def send_voice_request(self):
        print("\nListening for your voice (pretend voice input)...")  # Optional: Add your STT code here
        # (This is where Deepgram or microphone code would normally process)
        pass

    async def send_text_request(self, text):
        if not text.strip():
            return
        message = {"text": text}
        await self.ws.send(json.dumps(message))

def run():
    client = Client()
    asyncio.run(client.connect())
