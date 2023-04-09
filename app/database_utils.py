from datetime import datetime
from auth_vars import db1_details, db2_details

from pymongo import MongoClient
import psycopg2

db2_conn = psycopg2.connect(**db2_details)


db1_conn = MongoClient(db1_details)
db1 = db1_conn.db1
db1_users = db1["users"]


def insert_price_feed(pd):
    # pd is price_feed_dictionary, just shortened for readability
    try:
        cur = db2_conn.cursor()
        print(pd["rates"])
        values = [(pd["target"], t, pd["timestamp"], p) for (t,p) in pd["rates"].items()]
        
        args = ",".join(cur.mogrify("(%s,%s,%s,%s)", i).decode('utf-8') for i in values)

        cur.execute("INSERT INTO price_feed_checks (target, token, time_stamp, price) VALUES " + args)
        db2_conn.commit()
        cur.close()
        return True
    except:
        return False
