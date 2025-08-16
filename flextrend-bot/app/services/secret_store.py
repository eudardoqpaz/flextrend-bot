import os
from cryptography.fernet import Fernet, InvalidToken
from hashlib import sha256
import base64

MASTER = os.getenv("SECRET_KEY", "please_change_me").encode()
FERNET_KEY = sha256(MASTER).digest()
FERNET = Fernet(base64.urlsafe_b64encode(FERNET_KEY))

def encrypt(value: str) -> str:
    return FERNET.encrypt(value.encode()).decode()

def decrypt(value: str):
    try:
        return FERNET.decrypt(value.encode()).decode()
    except InvalidToken:
        return None
