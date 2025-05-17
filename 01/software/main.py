from yaspin import yaspin
spinner = yaspin()
spinner.start()

import typer
import ngrok
import platform
import threading
import os
import importlib
import subprocess
import webview
import socket
import json
import segno
from livekit import api
import time
from dotenv import load_dotenv
import signal
import warnings
import requests

# Load environment variables first
load_dotenv()

# Force environment TTS settings (good to have)
os.environ["INTERPRETER_TTS"] = "openai"
os.environ["TTS_ENGINE"] = "openai"

# Now import server and worker modules
from source.server.server import start_server
from source.server.livekit.worker import main as worker_main
from source.server.livekit.multimodal import main as multimodal_main

system_type = platform.system()

app = typer.Typer()

@app.command()
def run(
    server: str = typer.Option(None, "--server", help="Run server (accepts `livekit` or `light`)"),
    server_host: str = typer.Option("0.0.0.0", "--server-host", help="Server host"),
    server_port: int = typer.Option(10101, "--server-port", help="Server port"),
    expose: bool = typer.Option(False, "--expose", help="Expose server over internet"),
    domain: str = typer.Option(None, "--domain", help="Custom ngrok domain"),
    client: str = typer.Option(None, "--client", help="Run client (default `light-python`)"),
    server_url: str = typer.Option(None, "--server-url", help="Server URL (default auto-generated)"),
    qr: bool = typer.Option(False, "--qr", help="Display QR code connection info"),
    profiles: bool = typer.Option(False, "--profiles", help="Open profiles folder"),
    profile: str = typer.Option("default.py", "--profile", help="Specify profile file"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    multimodal: bool = typer.Option(False, "--multimodal", help="Enable multimodal agent"),
):

    threads = []

    if not server and not client:
        server = "light"
        client = "light-python"

    ### PROFILES

    profiles_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "source", "server", "profiles")

    if profiles:
        if platform.system() == "Windows":
            subprocess.Popen(['explorer', profiles_dir])
        elif platform.system() == "Darwin":
            subprocess.Popen(['open', profiles_dir])
        elif platform.system() == "Linux":
            subprocess.Popen(['xdg-open', profiles_dir])
        else:
            subprocess.Popen(['open', profiles_dir])
        exit(0)

    if profile:
        if not os.path.isfile(profile):
            profile = os.path.join(profiles_dir, profile)
            if not os.path.isfile(profile):
                profile += ".py"
                if not os.path.isfile(profile):
                    print(f"Invalid profile path: {profile}")
                    exit(1)

    # Load the profile module
    spec = importlib.util.spec_from_file_location("profile", profile)
    profile_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(profile_module)

    # Get the interpreter from the profile
    interpreter = profile_module.interpreter

    # 💥 FORCE Jessamy to use OpenAI TTS (critical fix)
    interpreter.tts = "openai"

    ### SERVER

    if system_type == "Windows":
        server_host = "localhost"

    if not server_url:
        server_url = f"{server_host}:{server_port}"

    if server:

        if server == "light":
            light_server_port = server_port
            light_server_host = server_host
            voice = True
        elif server == "livekit":
            spinner.stop()
            print(f"Starting light server (required for livekit) on port {server_port-1}")
            light_server_port = os.getenv('AN_OPEN_PORT', server_port-1)
            light_server_host = "localhost"
            voice = False

        server_thread = threading.Thread(
            target=start_server,
            args=(light_server_host, light_server_port, interpreter, voice, debug),
        )
        spinner.stop()
        print("Starting server...")
        server_thread.start()
        threads.append(server_thread)

        if server == "livekit":
            def run_command(command):
                subprocess.run(command, shell=True, check=True)

            if debug:
                command = f'livekit-server --dev --bind "{server_host}" --port {server_port}'
            else:
                command = f'livekit-server --dev --bind "{server_host}" --port {server_port} > /dev/null 2>&1'
            livekit_thread = threading.Thread(target=run_command, args=(command,))
            time.sleep(7)
            livekit_thread.start()
            threads.append(livekit_thread)
            local_livekit_url = f"ws://{server_host}:{server_port}"

        if expose:
            listener = ngrok.forward(f"{server_host}:{server_port}", authtoken_from_env=True, domain=domain)
            url = listener.url()
        else:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
            s.close()
            url = f"http://{ip_address}:{server_port}"

        if server == "livekit":
            print("Livekit server will run at:", url)

    ### CLIENT

    if client:
        module = importlib.import_module(f".clients.{client}.client", package="source")
        client_thread = threading.Thread(target=module.run, args=[server_url, debug])
        spinner.stop()
        print("Starting client...")
        client_thread.start()
        threads.append(client_thread)

    ### WAIT FOR THREADS TO FINISH

    def signal_handler(sig, frame):
        print("Termination signal received. Shutting down...")
        for thread in threads:
            if thread.is_alive():
                subprocess.run(f"pkill -P {os.getpid()}", shell=True)
        os._exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        for attempt in range(10):
            try:
                response = requests.get(url)
                status = "OK" if response.status_code == 200 else "Not OK"
                if status == "OK":
                    break
            except requests.RequestException:
                pass
            time.sleep(1)
        else:
            raise Exception(f"Server at {url} failed to respond after 10 attempts")

        if qr:
            def display_qr_code():
                time.sleep(10)
                content = json.dumps({"livekit_server": url})
                qr_code = segno.make(content)
                qr_code.terminal(compact=True)
            qr_thread = threading.Thread(target=display_qr_code)
            qr_thread.start()
            threads.append(qr_thread)

        if server == "livekit":
            time.sleep(1)
            os.environ['INTERPRETER_SERVER_HOST'] = light_server_host
            os.environ['INTERPRETER_SERVER_PORT'] = str(light_server_port)
            os.environ['01_TTS'] = interpreter.tts
            os.environ['01_STT'] = interpreter.stt

            token = str(api.AccessToken('devkey', 'secret') \
                .with_identity("identity") \
                .with_name("my name") \
                .with_grants(api.VideoGrants(room_join=True, room="my-room")).to_jwt())

            meet_url = f'https://meet.livekit.io/custom?liveKitUrl={url.replace("http", "ws")}&token={token}\n\n'
            print("\nJoin video call for debugging:")
            print(meet_url)

            for attempt in range(30):
                try:
                    if multimodal:
                        multimodal_main(local_livekit_url)
                    else:
                        worker_main(local_livekit_url)
                except KeyboardInterrupt:
                    print("Exiting.")
                    raise
                except Exception as e:
                    print(f"Error occurred: {e}")
                print("Retrying...")
                time.sleep(1)

        for thread in threads:
            thread.join()

    except KeyboardInterrupt:
        os.kill(os.getpid(), signal.SIGINT)
