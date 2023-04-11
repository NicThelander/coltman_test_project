from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import logging
# from typing import Annotated
from .utils import (create_token,
                    register_user,
                    auth_user,
                    decrypt_token,
                    auth_token_validity)
from .models import Registration, Login, PriceFeeds
from .database_utils import db2_conn, db1_users, insert_price_feed, retrieve_price_feed


security = HTTPBearer()

app = FastAPI()


# set up connections in database_utils instead of startup event here for less clutter.

@app.on_event("shutdown")
def shutdown_db_client():
    db2_conn.close()


# Filters out /health/ terminal spam when running the health checks
class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.args and len(record.args) >= 3 and record.args[2] != "/health"

# Add filter to the logger
logging.getLogger("uvicorn.access").addFilter(EndpointFilter())

# for docker health check (make sure node caller happens after)
@app.get("/health")
async def health():
    return "up"


# returns 200 registered successfully if all in order
@app.post("/register")
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
@app.post("/login")
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
@app.get("/get_all_users")
async def get_all_users(credentials: HTTPAuthorizationCredentials=Depends(security)):
     # don't really need the if here since it raises error on failure but doing it for clarity
    if auth_token_validity(credentials):
        # fastapi struggles to process the _id without some conversions but since it shouldn't be needed here, I opted to leave it out. have the password explicitly enabled here for testing registration etc during next interview but assume we'd set this to 0 on an actual API (depending on use case)
        return list(db1_users.find({}, {"_id": 0, "password": 1}))
    

@app.post("/fetch_price_feeds")
async def fetch_price_feeds(price_feeds: PriceFeeds, credentials: HTTPAuthorizationCredentials=Depends(security)):
    price_feeds_dict = price_feeds.dict()
    # thought it might be a bit more consolidated to just use post and store it straight into db2 with a try inside where I could also include a failure in logs if it fails to insert (although it would be pretty straightforward to store in db1 too).
    # don't really need the if here since it raises error on failure but doing it for clarity
    if auth_token_validity(credentials):
        if insert_price_feed(price_feeds_dict):
            return "inserted successfully"
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not submit to database")



@app.get("/get_price_feeds")
async def get_price_feeds(timestamp: int, credentials: HTTPAuthorizationCredentials=Depends(security)):
    if auth_token_validity(credentials):
        return retrieve_price_feed(timestamp)
    else:
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not retrieve from database")
