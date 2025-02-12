import base64
import hashlib
import hmac


def calculate_secret_hash(username: str, client_id: str, client_secret: str) -> str:
    msg = username + client_id
    message = bytes(msg, "utf-8")
    key = bytes(client_secret, "utf-8")
    return base64.b64encode(
        hmac.new(key, message, digestmod=hashlib.sha256).digest()
    ).decode()
