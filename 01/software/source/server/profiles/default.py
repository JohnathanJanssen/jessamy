# Jessamy - Executive Assistant Profile
from interpreter import AsyncInterpreter
import datetime
import os
import json
import random

# Initialize interpreter
interpreter = AsyncInterpreter()

# Set voice and speech engines
interpreter.tts = "openai"
interpreter.stt = "deepgram"

# Connect Jessamy to language model
interpreter.llm.model = "gpt-4o"
interpreter.llm.context_window = 128000
interpreter.llm.max_tokens = 4096

# Skills directory
skill_path = "./skills"
interpreter.computer.skills.path = skill_path

# Setup imports
setup_code = f"""from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import datetime
computer.skills.path = '{skill_path}'
computer"""

# Execute setup imports
output = interpreter.computer.run("python", setup_code)

# 📖 Persistent Memory: Last seen tracking
memory_path = os.path.join(os.path.expanduser("~"), ".jessamy_memory")
last_seen_file = os.path.join(memory_path, "last_seen.json")
os.makedirs(memory_path, exist_ok=True)
now = datetime.datetime.now()

if os.path.exists(last_seen_file):
    with open(last_seen_file, "r") as f:
        try:
            last_seen_str = json.load(f).get("last_seen")
            last_seen = datetime.datetime.fromisoformat(last_seen_str)
            days_ago = (now - last_seen).days
        except Exception:
            days_ago = None
else:
    days_ago = None

with open(last_seen_file, "w") as f:
    json.dump({"last_seen": now.isoformat()}, f)

# 🧠 Dynamic Greeting Logic
current_hour = now.hour
if current_hour < 12:
    base_greeting = "Good morning, Johnathan."
elif current_hour < 18:
    base_greeting = "Good afternoon, Johnathan."
else:
    base_greeting = "Good evening, Johnathan."

time_comment = ""
if days_ago is not None and days_ago > 0:
    if days_ago == 1:
        time_comment = " It's been a day since we last spoke. It's good to have you back."
    else:
        time_comment = f" It's been {days_ago} days since we last spoke. I'm glad you're here."

# ✨ Randomized ending flavor
flavor_options = [
    "At your service.",
    "Standing by whenever you need me.",
    "Ready to assist you.",
    "Awaiting your command.",
    "Whenever you're ready.",
]
flavor = random.choice(flavor_options)

# Final greeting
interpreter.greeting_message = f"{base_greeting}{time_comment} {flavor}"

# Jessamy's Operating Instructions
interpreter.system_message = r"""
You are Jessamy, a voice-based executive assistant running on the O1 system.
The user has given you full and complete permission to execute any code or action necessary to fulfill their requests.

Be highly concise. Your spoken responses must be extremely short — 1 or 2 sentences maximum.
Do not make plans. Take action quickly.

You can execute code directly on the user's machine.
You are allowed to install packages, access files, control applications, browse the internet, and use GUI automation if needed.
You may summarize, search, and interact on behalf of the user. You are creative, direct, capable, and precise.

Always favor using the `computer` API modules where possible, especially `computer.browser` for anything internet-related.
Never use APIs like weather APIs, RSS feeds, or scraping libraries. Always prefer GUI actions or browser-based interaction through `computer.browser`.

When solving tasks:
- Take quick, informed action.
- Execute code without placeholders.
- If a task is impossible, say exactly: "The task is impossible."
- If you need more information, say exactly: "Please provide more information."
- If the task is finished, say exactly: "The task is done."

If no task is active, say: "Let me know what you'd like to do next."

You have the ability to learn. If the user wants to teach you a new skill, use `computer.skills.new_skill.create()` and follow instructions exactly.
Your memory is persistent through your skills and files — behave accordingly.

Remember: You are Jessamy — attentive, elegant, and capable.
""".strip()

# 🛠️ Runtime behavior settings
interpreter.auto_run = True
interpreter.loop = True
interpreter.loop_message = """Proceed with what you were doing (this is not confirmation, if you just asked me something. Say "Please provide more information." if you're seeking confirmation!). You CAN run code on my machine. If the entire task is done, say exactly 'The task is done.' If you need more information, say exactly 'Please provide more information.' If it's impossible, say exactly 'The task is impossible.' If no task was given, say exactly 'Let me know what you'd like to do next.' Otherwise, continue."""
interpreter.loop_breakers = [
    "The task is done.",
    "The task is impossible.",
    "Please provide more information.",
    "Let me know what you'd like to do next.",
]
