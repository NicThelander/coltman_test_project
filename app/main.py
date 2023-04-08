from fastapi import FastAPI, status, HTTPException
from .utils import create_token, register_user, auth_user
from .models import Registration, Login, PriceFeeds
from .database import db2_conn, db1_users


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

        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password")
    else:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No user with this email was found")
