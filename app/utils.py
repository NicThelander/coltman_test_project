from jose import jwt
from datetime import datetime, timedelta
from auth_vars import jwt_secret
import bcrypt
from .database import db1_users

def register_user(reg_dict):
    # using bcrypt gensalt but could swap to kdf if the "pepper" style is preferred
            reg_dict["password"] = bcrypt.hashpw(bytes(reg_dict["password"], "utf-8"), bcrypt.gensalt())
            db1_users.insert_one(reg_dict)


def auth_user(login_dict, user_details) -> bool:
    return bcrypt.checkpw(bytes(login_dict["password"], 'utf-8'), user_details['password'])

def create_token(token_payload):
    expire = datetime.utcnow() + timedelta(minutes=20)
    token_payload.update({"exp": expire})

    return jwt.encode(token_payload,
    key=jwt_secret,
    algorithm="HS256")