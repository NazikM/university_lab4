import re
from datetime import timedelta, datetime

import bcrypt
import jwt

from settings import ALGORITHM, SECRET_KEY


def check_password(password):
    """Returns True is password is good vise versa False"""
    if len(password) < 8:
        return False

    if not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password):
        return False

    if not re.search(r'\d', password):
        return False

    if not re.search(r'[^A-Za-z\d]', password):
        return False
    return True


def hash_password(password: str) -> str:
    # Hash a password using bcrypt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Check if the plain password matches the hashed password
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


# Function to create JWT token
def create_jwt_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(weeks=1)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Function to decode JWT token
def decode_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
    except Exception:
        raise ValueError("Could not validate credentials")
