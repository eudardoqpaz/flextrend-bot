import requests
from config import SETTINGS

def tg_send(text: str):
    if not SETTINGS.telegram_bot_token or not SETTINGS.telegram_chat_id:
        return
    url = f"https://api.telegram.org/bot{SETTINGS.telegram_bot_token}/sendMessage"
    try:
        requests.post(url, json={"chat_id": SETTINGS.telegram_chat_id, "text": text})
    except Exception:
        pass
