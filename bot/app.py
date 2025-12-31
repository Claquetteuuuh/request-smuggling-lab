import requests
import time
import threading

HOST = "frontend"
PORTS = [8001, 8002, 8003]
COOKIE = {"secret": "CgcWgAPyfrG5JZpPrFQ1YJPzF7G1obUT"}

def run_bot():
    print("Bot started...")
    while True:
        try:
            # Single Target (Port 80 internal)
            url = f"http://{HOST}/admin"
            # Add padding to ensure the request is long enough to satisfy the smuggled Content-Length (1500)
            # preventing the backend from hanging while waiting for more data.
            # IMPORTANT: Put Cookie BEFORE Padding to ensure it's captured in the smuggled part!
            headers = {
                "Cookie": f"secret={COOKIE['secret']}",
                "X-Padding": "A" * 2000
            }
            # Remove cookies= arg to avoid dupe/reordering
            requests.get(url, headers=headers, timeout=2)
        except Exception as e:
            pass
        time.sleep(5)

if __name__ == "__main__":
    # Delay to let services start
    time.sleep(5)
    run_bot()
