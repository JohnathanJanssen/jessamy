import threading
import time
import requests
import webview
from app import app  # Import the Flask app

def run_server():
    app.run(debug=True, port=5001)

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
    # Start the Flask server in a background thread
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    # Wait until the Flask server is ready
    wait_for_server('http://127.0.0.1:5001')

    # Create the webview window
    webview.create_window('Jessamy', 'http://127.0.0.1:5001', width=1000, height=800)
    webview.start()