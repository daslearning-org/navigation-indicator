import subprocess
import json
import requests
import time

last_notification = ""
loop_break = "no"
api_url = "http://127.0.0.1:8089/nav/"

def get_termux_notifications():
    try:
        # Run the command and capture the output
        result = subprocess.run(
            ['termux-notification-list'], 
            capture_output=True, 
            text=True, 
            check=True
        )

        # Parse the JSON string into a Python list
        notifications = json.loads(result.stdout)
        return notifications

    except subprocess.CalledProcessError as e:
        print(f"Error calling Termux API: {e}")
        return None
    except json.JSONDecodeError:
        print("Failed to parse notification JSON.")
        return None

def send_nav_api(title:str, text:str=""):
    try:
        requests.post(
            api_url,
            json={"title": title, "text": text}
        )
    except Exception as e:
        print(f"An API error: {e}")

while True:
    notifications = get_termux_notifications()
    if notifications:
        for noti in notifications:
            pkg_name = noti.get('packageName')
            noti_title = noti.get('title')
            noti_text = noti.get('content')
            if pkg_name == "net.osmand" and noti_title != last_notification:
                send_nav_api(noti_title, noti_text)
                print(f"{noti_title, noti_text}")
                last_notification = noti_title
                break # no need to check other nitifications

    time.sleep(1)
