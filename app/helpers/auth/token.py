import os
from dotenv import load_dotenv

load_dotenv()

from datetime import datetime, timedelta
from jose import jwt, ExpiredSignatureError

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
REFRESH_TOKEN_EXPIRE_DAYS = os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")

def create_jwt_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)



def create_access_token(data: dict):
    return create_jwt_token(data, timedelta(minutes=float(ACCESS_TOKEN_EXPIRE_MINUTES)))

def create_refresh_token(data: dict):
    return create_jwt_token(data, timedelta(days=(float(REFRESH_TOKEN_EXPIRE_DAYS))))

def decode_access_token(token: str):
    try:
        decode = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decode
    except ExpiredSignatureError:
        return None
    except Exception:
        return None
