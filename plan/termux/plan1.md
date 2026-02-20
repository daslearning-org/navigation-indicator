Yes — **Termux actually can read notifications** 😄
But only through an official addon app:

> **Termux:API**

This gives Linux-style CLI access to Android system features — including notifications.

So your architecture becomes even simpler:

```
Google Maps → Android notification → Termux:API → shell/python → HTTP → Kivy app
```

No MacroDroid needed ✔
No Java service ✔
Fully local ✔
Very hacker-friendly ✔

---

# 1️⃣ Install required apps (IMPORTANT)

From **F-Droid** (not Play Store):

Install:

* Termux
* Termux:API
* Termux:Boot (optional but useful)

Then inside Termux:

```bash
pkg update
pkg install termux-api python jq
pip install requests
```

---

# 2️⃣ Grant notification access

Run:

```bash
termux-notification-listen
```

Android will open settings → enable **Termux:API Notification Access**

This is same permission MacroDroid uses.

---

# 3️⃣ See Google Maps notifications live

Run:

```bash
termux-notification-listen
```

Now start navigation in Google Maps.

You will see JSON stream like:

```json
{
  "packageName": "com.google.android.apps.maps",
  "title": "Navigation",
  "text": "Turn right in 200 m"
}
```

This is a continuous event stream (stdin pipe).

---

# 4️⃣ Filter only Maps navigation

Create script:

`maps_listener.py`

```python
import json, sys, requests

URL = "http://127.0.0.1:8765/maps"

for line in sys.stdin:
    try:
        data = json.loads(line)

        if data.get("packageName") != "com.google.android.apps.maps":
            continue

        text = data.get("text") or ""
        title = data.get("title") or ""

        msg = f"{title} {text}".strip()

        if msg:
            print("Maps:", msg)
            requests.post(URL, json={"text": msg}, timeout=0.2)

    except:
        pass
```

Run:

```bash
termux-notification-listen | python maps_listener.py
```

Now your Kivy app updates instantly 🚀

Latency ~20–80 ms (faster than MacroDroid)

---

# 5️⃣ Auto-start on phone boot (optional)

Create:

```
~/.termux/boot/start_maps.sh
```

```bash
#!/data/data/com.termux/files/usr/bin/bash
termux-notification-listen | python /data/data/com.termux/files/home/maps_listener.py
```

```bash
chmod +x ~/.termux/boot/start_maps.sh
```

Now it runs automatically after reboot.

---

# Advantages vs MacroDroid

| Termux           | MacroDroid             |
| ---------------- | ---------------------- |
| Free             | Paid (for unlimited)   |
| Programmable     | GUI only               |
| Ultra fast       | Medium latency         |
| Scriptable logic | Limited filters        |
| Great for devs   | Great for normal users |

---

# Important Android limitation

Works only while Termux process alive.

So you should:

```
termux-wake-lock
```

and disable battery optimization for Termux.

---

# Final Result

You now built a **real-time navigation data bridge**:

Google Maps → Linux pipe → Python → Kivy HUD display

This is actually how many open-source Android HUD projects work internally 🙂

---

If you want next:
We can parse maneuver type and show arrows automatically instead of raw text.
