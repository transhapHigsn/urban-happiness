from datetime import datetime, timezone, timedelta
from hashlib import sha256

import jwt
from tracker.constants import JWT_SECRET, SYSTEM_SECRET


def get_time():
    return datetime.now(timezone.utc)


def create_hash(name, email, secret):
    message = (
        f"?name={name}&&email={email}&&secret={secret}&&system_secret={SYSTEM_SECRET}"
    )
    digest = sha256(message.encode()).hexdigest()
    return digest


def encode_auth_token(user_id):
    """
    Generates the Auth Token
    :return: dict
    """
    payload = {
        "exp": datetime.utcnow() + timedelta(days=0, seconds=900),
        "iat": datetime.utcnow(),
        "sub": user_id,
    }
    return {
        "success": True,
        "data": {"access_token": jwt.encode(payload, JWT_SECRET, algorithm="HS256")},
    }


def decode_auth_token(auth_token):
    """
    Decodes the auth token
    :param auth_token:
    :return: dict
    """
    try:
        payload = jwt.decode(auth_token, JWT_SECRET)
        return {"success": True, "data": {"user_id": payload["sub"]}}
    except jwt.ExpiredSignatureError:
        return {"success": False, "message": "Signature expired. Please log in again."}
    except jwt.InvalidTokenError:
        return {"success": False, "message": "Invalid token. Please log in again."}
