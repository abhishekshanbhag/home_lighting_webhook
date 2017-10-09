#!/usr/bin/env python

import urllib
import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = makeWebhookResult(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def makeWebhookResult(req):
    if req.get("result").get("action") != "home.connect":
        return {"speech": "I'm only testing",
        "displayText": "I'm only testing",
        #"data": {},
        # "contextOut": [],
        "source": "my_server"}
    result = req.get("result")
    parameters = result.get("parameters")
    zone = parameters.get("mode")

    cost = {'Europe':100, 'North America':200, 'South America':300, 'Asia':400, 'Africa':500}

    speech = "Your device is connected"

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        #"data": {},
        # "contextOut": [],
        "source": "my_server"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8004))

    print("Starting app on port", str(8004))



    app.run(debug=True, port=port, host="0.0.0.0")
