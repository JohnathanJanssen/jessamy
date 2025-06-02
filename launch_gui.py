import threading
import time
import requests
import webview
from app import app

def run_server():
    app.run(debug=False, port=5001, use_reloader=False)

def wait_for_server(url):
    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                break
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)

if __name__ == '__main__':
    # Run Flask server in background
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    # Wait for Flask server to be ready
    wait_for_server('http://127.0.0.1:5001')

    # Launch web GUI
    webview.create_window('Jessamy', 'http://127.0.0.1:5001', width=1000, height=800)
    webview.start()
