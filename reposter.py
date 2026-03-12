import os
import re
import base64
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from telethon import TelegramClient, events
from dotenv import load_dotenv


# -----------------------------
# Health server for Render
# -----------------------------
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Telethon bot running")

    # prevent HEAD 501 warnings
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()


def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    print(f"Health server running on port {port}")
    server.serve_forever()


threading.Thread(target=run_health_server, daemon=True).start()


# -----------------------------
# Load configuration
# -----------------------------
load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
phone = os.getenv("PHONE")
session_data = os.getenv("TELETHON_SESSION")

print("Session env exists:", bool(session_data))

if session_data:
    with open("session.session", "wb") as f:
        f.write(base64.b64decode(session_data))
    print("Session file restored")

sources = [c.strip() for c in os.getenv("SOURCE_CHANNELS").split(",")]
target = os.getenv("TARGET_CHANNEL")
prefix = os.getenv("PREFIX_TEXT")

print("Sources:", sources)
print("Target:", target)


# -----------------------------
# Telegram client
# -----------------------------
client = TelegramClient("session", api_id, api_hash)


def looks_like_code(text: str):
    if not text:
        return False

    text = text.strip()

    if len(text) > 10:
        return False

    if not re.match(r'^[A-Za-z0-9]+$', text):
        return False

    if re.search(r'[aeiou]{3,}', text.lower()):
        return False

    return True


# -----------------------------
# Message listener
# -----------------------------
@client.on(events.NewMessage)
async def handler(event):
    chat = await event.get_chat()

    # only react to specified channels
    if getattr(chat, "username", None) not in sources:
        return

    text = event.raw_text
    print("Incoming:", text)

    if not looks_like_code(text):
        print("Filtered")
        return

    new_text = f"{prefix}\n\n{text}"

    try:
        await client.send_message(target, new_text)
        print("Posted:", text)
    except Exception as e:
        print("Failed:", e)


print("Event handler registered")


# -----------------------------
# Main loop
# -----------------------------
async def main():
    print("Starting Telethon reposter...")
    await client.start(phone=phone)

    print("Telethon connected!")

    dialogs = await client.get_dialogs()
    print("Account dialogs:", [d.name for d in dialogs[:10]])

    print("Listening for messages...")
    await client.run_until_disconnected()


client.loop.run_until_complete(main())