from fastapi import FastAPI, status, HTTPException, Header, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Annotated
from .utils import (create_token,
                    register_user,
                    auth_user,
                    decrypt_token,
                    check_auth_token)
from .models import Registration, Login, PriceFeeds
from .database import db2_conn, db1_users
from datetime import datetime

security = HTTPBearer()

app = FastAPI()


# @app.on_event("startup")
# def startup_db_client():
#     app.mongodb_client = MongoClient(db1_details)
#     app.db1 = app.mongodb_client["db1"]
#     # app.db2 = connectdb2()
#     print("connected")

# @app.on_event("shutdown"):
# def shutdown_db_client():
#     app.mongodb_client.close()
#     # app.db2_conn.close()
#     print("done")


@app.get("/")
async def root():
        return {"message": "test"}


@app.post("/register/")
async def register(registration: Registration):
    reg_dict = registration.dict()
    # checks if there are any rows with given email
    if list(db1_users.find({"email": reg_dict["email"]})):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="email address already registered")
    else:
        try:
            register_user(reg_dict)
            return "registered successfully"
        except:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something went wrong with submitting user info")


@app.post("/login/")
async def login(login: Login):
    login_dict = login.dict()
    user_details = db1_users.find_one({"email": login_dict["email"]})

    if user_details:
        if auth_user(login_dict, user_details):
            return {"access_token": create_token({"email": user_details["email"]}),
            "token_type": "bearer"}
        else:
            raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect password")
    else:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No user with this email was found")

@app.get("/get_all_users/")
async def get_all_users(credentials: HTTPAuthorizationCredentials= Depends(security)):
    return check_auth_token(credentials)
    

    # if datetime.utcnow() <= jwt_dict["exp"]:
    #     return "in the Nic of time"
    # else:
    #     return "not in the Nic of time"
