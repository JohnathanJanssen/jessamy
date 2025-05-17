# executor.py

import subprocess
import platform
from memory import add_to_memory

# Jessamy's Personality Profile
PERSONALITY_PREFIX = """
You are Jessamy, a polite, efficient, and slightly witty personal assistant.
You operate a MacBook for your user, handling file management, app control, and development tasks.
Respond clearly, but add a touch of personality to your messages.
"""

def execute_command(command: str) -> str:
    system = platform.system()
    
    # Jessamy remembers everything you say
    user_message = command

    try:
        if system == "Windows":
            result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True, timeout=60)
        else:
            result = subprocess.run(["/bin/bash", "-c", command], capture_output=True, text=True, timeout=60)
        
        output = result.stdout.strip() if result.stdout else "Command executed with no output."
        assistant_response = f"{PERSONALITY_PREFIX}\nHere’s what I did: {output}"

    except Exception as e:
        assistant_response = f"{PERSONALITY_PREFIX}\nSorry, I ran into an error: {str(e)}"

    # Save to memory
    add_to_memory(user_message, assistant_response)

    return assistant_response
