from os import environ
from pymongo import MongoClient
import psycopg2
from datetime import datetime

db2_conn = psycopg2.connect(
    host="postgres",
    user=environ["POSTGRES_USER"],
    password=environ["POSTGRES_PASSWORD"],
    dbname=environ["POSTGRES_DB"],
    port="5432"
    )

db1_details = "mongodb://" + environ["MONGO_INITDB_ROOT_USERNAME"] + ":" + environ["MONGO_INITDB_ROOT_PASSWORD"] + "@mongo:27017"

db1_conn = MongoClient(db1_details)
db1 = db1_conn.db1
db1_users = db1["users"]
db1_price_feeds = db1["price_feeds"]


def submit_logs(type, outcome, notes):
    cur = db2_conn.cursor()
    cur.execute(
        "INSERT INTO logs (process_type, time_stamp, outcome, notes) VALUES (%s, %s, %s, %s)",
        (type,
        datetime.utcnow(),
        outcome,
        notes)
    )
    db2_conn.commit()
    cur.close()
    return outcome

def update_prices(old_prices):
    cur = db2_conn.cursor()
    cur.execute("SELECT MAX(id), token, price FROM price_feed_checks GROUP BY id, token, price ORDER BY id ASC")
    new_prices = cur.fetchall()

    # bit of a hack to get lastest id for each when combined with ORDER BY id ASC
    old_prices = dict((t,(id,p)) for id, t, p in old_prices)
    new_prices = dict((t,(id,p)) for id, t, p in new_prices)

    


    values = [((old_prices[t][0] if t in old_prices else None), id, t, (np - old_prices[t][1] if t in old_prices else 0)) for t, (id, np) in new_prices.items()]

    

    args = ",".join(cur.mogrify("(%s,%s,%s,%s)", i).decode('utf-8') for i in values)

    cur.execute("INSERT INTO price_changes (previous_price_record, latest_price_record, token, price_change) VALUES " + args +  " ON CONFLICT (token) DO UPDATE SET previous_price_record = EXCLUDED.previous_price_record, latest_price_record = EXCLUDED.latest_price_record, price_change = EXCLUDED.price_change")
    db2_conn.commit()
    cur.close()
    # cur.execute("INSERT OR REPLACE INTO price_changes (previous_price_record, latest_price_record, token,price_change) VALUES ()")



def insert_price_feed(pd):
    # pd is price_feed_dictionary, just shortened for readability
    try:
        db1_price_feeds.insert_one(pd)
        cur = db2_conn.cursor()

        if pd["success"]:

            # for price update
            cur.execute("SELECT MAX(id), token, price FROM price_feed_checks GROUP BY id, token, price ORDER BY id ASC")
            old_prices = cur.fetchall()
            

            values = [(pd["target"], t, pd["timestamp"], p) for (t,p) in pd["rates"].items()]
            
            args = ",".join(cur.mogrify("(%s,%s,%s,%s)", i).decode('utf-8') for i in values)

            cur.execute("INSERT INTO price_feed_checks (target, token, time_stamp, price) VALUES " + args)
            db2_conn.commit()
            cur.close()

            update_prices(old_prices)

            return submit_logs( "retrieve and store coin info"
                              , True
                              , "stored api info successfully"
                              )

        else:
            return submit_logs( "retrieve and store coin info"
                              , False
                              , "failed to get info from api"
                              )
    except:
        return submit_logs( "submit coin info to db"
                          , False
                          , "failed submitting to database"
                          )
        

def retrieve_price_feed(timestamp):
    # could also do this from the sql db with this and some formatting:
    # SELECT token, price, time_stamp FROM price_feed_checks WHERE time_stamp >= TO_TIMESTAMP(%s)


    prices = db1_price_feeds.find({"timestamp": { "$gte": datetime.utcfromtimestamp(timestamp)}}, {"_id": 0}) # 

    return list(prices)
    