import fetch from 'node-fetch';
import 'dotenv/config';



// get info from coinlayer api
// const response = await fetch('http://api.coinlayer.com/live?access_key=' + process.env.coinlayer_api_key,{
//     method: 'POST'});

// const data = await response.json();



// // // format and post the info to fetch price feeds
// const body = {
//     "timestamp": data["timestamp"],
//     "target": data["target"],
//     "rates": data["rates"]
// };

// console.log(body);

const test_data = {"success": true}

const body = {
    "timestamp": 1681072447,
    "target": 'USD',
    "rates": {
        USDT: 1.00092,
        UTT: 0.013,
        UQC: 8
    },
};

// // will need to add some if fail stuff here and in coinlayer part

const python_api_response = await fetch('http://api:8000/fetch_price_feeds/', {
    method: 'post',
    body: JSON.stringify(body),
    headers: {'Content-Type': 'application/json'}
});

const python_api_data = await python_api_response.json();

console.log(python_api_data);




