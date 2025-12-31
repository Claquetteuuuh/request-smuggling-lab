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
            requests.get(url, cookies=COOKIE, timeout=2)
        except Exception as e:
            pass
        time.sleep(5)

if __name__ == "__main__":
    # Delay to let services start
    time.sleep(5)
    run_bot()
