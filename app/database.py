from auth_vars import db1_details, db2_details

from pymongo import MongoClient
import psycopg2

db2_conn = psycopg2.connect(**db2_details)


db1_conn = MongoClient(db1_details)
db1 = db1_conn.db1
db1_users = db1["users"]