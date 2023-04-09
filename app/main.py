from fastapi import FastAPI, status, HTTPException, Header, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Annotated
from .utils import (create_token,
                    register_user,
                    auth_user,
                    decrypt_token,
                    auth_token_validity)
from .models import Registration, Login, PriceFeeds
from .database_utils import db2_conn, db1_users, insert_price_feed, retrive_price_feed
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


# @app.get("/")
# async def root():
#         return {"message": "test"}


# returns 200 registered successfully if all in order
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


# returns a jwt on success
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

# returns user collection if authorized
@app.get("/get_all_users/")
async def get_all_users(credentials: HTTPAuthorizationCredentials= Depends(security)):
     # don't really need the if here since it raises error on failure but doing it for clarity
    if auth_token_validity(credentials):
        # fastapi struggles to process the _id without some conversions but since it shouldn't be needed here, I opted to leave it out. have the password explicitly enabled here for testing registration etc during next interview but assume we'd set this to 0 on an actual API (depending on use case)
        return list(db1_users.find({}, {"_id": 0, "password": 1}))
    

@app.post("/fetch_price_feeds/") # I think it makes a bit more sense for me to do a post here with the node info once structured
async def fetch_price_feeds(price_feeds: PriceFeeds):
    price_feeds_dict = price_feeds.dict()
    if insert_price_feed(price_feeds_dict):
        return "inserted successfully"
    else:
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not submit to database")

# @app.get("/get_price_feeds/")
# async def get_price_feeds():
