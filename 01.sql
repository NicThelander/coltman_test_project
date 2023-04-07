-- going to be using varchar without a length specified unless I can see
-- some consistent length, it's generally pretty performant these days.
CREATE TABLE IF NOT EXISTS price_feed_checks (
    id SERIAL PRIMARY KEY,-- could have also used bigserial here to be safer but
    -- doing one check every 5 mins will take around 20.4k years and I don't
    -- think this test project is that ambitious.
    target VARCHAR,
    time_stamp TIMESTAMP, -- timestamp is a keyword so rather using time_stamp
    price FLOAT
);

CREATE TABLE IF NOT EXISTS price_changes (
    id VARCHAR PRIMARY KEY,
    previous_price_record INT REFERENCES price_feed_checks (id),
    latest_price_record INT REFERENCES price_feed_checks (id),
    price_change FLOAT
);

CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    process_type VARCHAR,
    time_stamp TIMESTAMP,
    outcome BOOLEAN,
    notes VARCHAR
);
