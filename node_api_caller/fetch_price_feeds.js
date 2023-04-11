import fetch from 'node-fetch';
import 'dotenv/config';
import pg from 'pg';

const auth = process.env;



async function register() {
    // could store extra details in env but shouldn't matter for example code
    const body = {
        "email": auth.email,
        "password": auth.pw,
        "name": "irrelevant",
        "surname": "irrelevant",
        "mobile": "irrelevant"
    };

    return await fetch('http://api:8000/register', {
        method: 'post',
        body: JSON.stringify(body),
        headers: { 'Content-Type': 'application/json' }
    })
        .then(async (res) => {
            if (res.ok) {
                return await login();
            } else {
                throw res.statusText;
            }
        })
        .catch(error => {
            console.log(error);
        });

}

async function login() {
    const body = {
        "email": auth.email,
        "password": auth.pw
    };

    let hacky_registration = "";
    return await fetch('http://api:8000/login', {
        method: 'post',
        body: JSON.stringify(body),
        headers: { 'Content-Type': 'application/json' }
    })
        .then(async (res) => {
            if (res.ok) {
                return res;
            } else if (res.status == 404) {
                hacky_registration = await register();
                throw "registered";
            } else if (res.status == 401) {
                throw "Please correct password and restart docker\n";
            } else {
                throw res.statusText;
            }
        })
        .then(res => res.json())
        .then(res => {
            return res["access_token"];
        })
        .catch(error => {
            if (error === "registered") {
                return hacky_registration; // not sure if I like or hate this haha
            } else {
                console.log(error);
            }
        });

}

const jwt = await login();


const client = new pg.Client({
    host: 'postgres',
    port: 5432,
    database: auth.POSTGRES_DB,
    user: auth.POSTGRES_USER,
    password: auth.POSTGRES_PASSWORD,
});

// client.connect((err) => {
//     if (err) {
//         console.error('connection error', err.stack);
//     } else {
//         console.log('connected');
//     }
// })

const submit_script_log = async (process_type, outcome, notes) => {
    try {
        client.connect()
        await client.query(
            "INSERT INTO logs (process_type, time_stamp, outcome, notes) VALUES ($1, TO_TIMESTAMP($2), $3, $4)", [
            process_type,
            Math.floor(Date.now() / 1000),
            outcome,
            notes
        ]
        );
        client.end()
        return true;
    } catch (error) {
        console.error(error.stack);
    }
}




// get info from coinlayer api
const response = await fetch('http://api.coinlayer.com/live?access_key=' + process.env.coinlayer_api_key,{
    method: 'POST'});

if(!response.ok) {
    submit_script_log("calling coinlayer api", false, "failed to call the coinlayer api")
}

const data = await response.json();


// const data = { "success": true }

if (data["success"] === false) {
    submit_script_log("coinlayer api gave failure", false, "coin api fail");
    console.log("something went wrong with coinlayer api, please check issue and retry, caller script won't continue past this point otherwise");
} else {

    // const body = {
    //     "timestamp": 1681072447,
    //     "target": 'USD',
    //     "rates": {
    //         USDT: 1.00092,
    //         UTT: 0.013,
    //         UQC: 8
    //     },
    //     "success": true
    // };

    // // // format and post the info to fetch price feeds
    const body = {
        "timestamp": data["timestamp"],
        "target": data["target"],
        "rates": data["rates"],
        "success": data["success"]
    };



    const python_api_response = await fetch('http://api:8000/fetch_price_feeds', {
        method: 'post',
        body: JSON.stringify(body),
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + jwt
        }
    }).catch(error => {
        submit_script_log("submitting feeds to api", false, "submission failed");
        console.log(error);
    });

    const python_api_data = await python_api_response.json();

    console.log(python_api_data);



    const price_feed = await fetch('http://api:8000/get_price_feeds?timestamp=' + body.timestamp, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + jwt
        }
    });

    const price_feed_data = await price_feed.json();

    console.log(price_feed_data);



    submit_script_log("caller script complete", true, "script run to completion").then(result => {
        if (result) {
            console.log("script log submitted");
        } else {
            console.log("something went wrong with submission");
        }
    })

}

