# server.py

import os
import json
import asyncio
import openai
import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from executor import execute_command

# === CONFIG ===
OPENAI_API_KEY = "sk-C3vfhClWI2c5Jxm_iIWQ5eDqtm_3qMQCASFB283v8rT3BlbkFJxWm9qO84UnMzRnkUTR90Y0pHMRjc5ouQSKgPogTSMA"

# === SERVER SETUP ===
app = FastAPI()

static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def get_index():
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            data = await websocket.receive_text()
            data = json.loads(data)
            user_message = data.get("content")

            print(f"Received from client: {user_message}")

            assistant_reply = await generate_reply(user_message)

            await websocket.send_text(json.dumps({
                "role": "assistant",
                "type": "message",
                "content": assistant_reply
            }))
        except Exception as e:
            print(f"Error: {e}")
            break

async def generate_reply(user_message):
    """Send message to OpenAI and determine if an action is needed."""
    try:
        response = await asyncio.to_thread(
            openai.ChatCompletion.create,
            model="gpt-4",
            messages=[
                {"role": "system", "content": (
                    "You are Jessamy, an intelligent assistant. "
                    "If the user asks you to do something on the system (open apps, create files, etc), "
                    "respond with a short explanation plus output an ACTION JSON block in this format:\n\n"
                    "{'action': 'open_app', 'details': {'app': 'Safari'}}\n"
                    "{'action': 'count_files', 'details': {'directory': '/Users/...'}}\n"
                    "{'action': 'create_file', 'details': {'filepath': '/path/to/file.txt', 'content': 'text here'}}\n"
                    "{'action': 'read_file', 'details': {'filepath': '/path/to/file.txt'}}\n"
                    "Otherwise, just talk normally without ACTION."
                )},
                {"role": "user", "content": user_message}
            ]
        )

        assistant_content = response['choices'][0]['message']['content']
        print(f"Assistant reply: {assistant_content}")

        # Try to extract and execute actions
        executed_result = None
        if "{'action':" in assistant_content:
            try:
                action_json = assistant_content.split("{'action':")[1]
                action_json = "{'action':" + action_json
                action_json = action_json.replace("'", '"')  # Fix JSON
                action_data = json.loads(action_json)

                executed_result = execute_command(
                    action_data.get("action"),
                    action_data.get("details", {})
                )
            except Exception as e:
                executed_result = f"(Failed to execute action: {e})"

        final_reply = assistant_content

        if executed_result:
            final_reply += f"\n\n{executed_result}"

        return final_reply

    except Exception as e:
        return f"Sorry, I had trouble processing your request: {e}"

# === MAIN START ===
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10101)