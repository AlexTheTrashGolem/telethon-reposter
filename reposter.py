import os
import re
from telethon import TelegramClient, events
from dotenv import load_dotenv
import base64
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Telethon bot running")

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    print(f"Health server running on port {port}")
    server.serve_forever()

threading.Thread(target=run_health_server, daemon=True).start()

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
phone = os.getenv("PHONE")
session_data = os.getenv("TELETHON_SESSION")

if session_data:
    with open("session.session", "wb") as f:
        f.write(base64.b64decode(session_data))

sources = os.getenv("SOURCE_CHANNELS").split(",")
target = os.getenv("TARGET_CHANNEL")
prefix = os.getenv("PREFIX_TEXT")

client = TelegramClient("session", api_id, api_hash)


def looks_like_code(text: str):
    if not text:
        return False

    text = text.strip()

    # shorter than 10 symbols
    if len(text) > 10:
        return False

    # only letters + numbers
    if not re.match(r'^[A-Za-z0-9]+$', text):
        return False

    # reject obvious dictionary words
    if re.search(r'[aeiou]{3,}', text.lower()):
        return False

    return True


@client.on(events.NewMessage(chats=sources))
async def handler(event):
    text = event.raw_text
    # Debug: confirm we receive messages
    print("Incoming:", text)
    if not looks_like_code(text):
        return

    new_text = f"{prefix}\n\n{text}"

    try:
        await client.send_message(target, new_text)
        print("Posted:", text)
    except Exception as e:
        print("Failed:", e)


async def main():
    print("Starting Telethon reposter...")
    await client.start(phone=phone)
    await client.run_until_disconnected()


client.loop.run_until_complete(main())