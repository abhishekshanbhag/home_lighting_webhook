#!/usr/bin/env python

import urllib
import json
import os
import socket


from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)

color_scheme = {"red": 5, "green": 6, "yellow": 7, "all": 18}

HOST_pi = "73.149.23.208"
PORT_pi = 40002
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST_pi,PORT_pi))


s.send(b"Reached Checkpoint1")
with open('comm/input.json') as doc:
    data = json.load(doc)
    U_ID = int(data['u_id'], 16)
    devices = data['devices']

s.send(b"Reached 2")


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    print("Request:")
    print(json.dumps(req, indent=4))
    s.send(b"Reached inside")
    res = makeWebhookResult(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def makeWebhookResult(req):
    data = s.recv(1024)
    socket_command = ""
    result = req.get("result")
    if result.get("action") == "home.connect":
        socket_command += "C "
        parameters = result.get("parameters")
        dev_id = parameters.get("number")
        if dev_id in devices:
            speech = "This device already exists. You cannot use two devices with the same name. Please choose a new name for this device."
            return {
                "speech": speech,
                "displayText": speech,
                #"data": {},
                # "contextOut": [],
                "source": "my_server"
                }
        else:
            socket_command += str(len(devices) + 1)
            devices[dev_id] = len(devices) + 1
            s.send(socket_command.encode())
            data = s.recv(1024)


        speech = data.decode()

        print("Response:")
        print(speech)

        return {
            "speech": speech,
            "displayText": speech,
            #"data": {},
            # "contextOut": [],
            "source": "my_server"
            }
    elif result.get("action") == "home.control":
        socket_command += "L "
        parameters = result.get("parameters")
        dev_id = parameters.get("number")
        if(not(dev_id in devices)):
            speech = "You haven't connected this device yet. Maybe you should do that first."
            return {
                "speech": speech,
                "displayText": speech,
                #"data": {},
                # "contextOut": [],
                "source": "my_server"
                }
        else:
            socket_command += str(dev_id) + " "
            bulbs = parameters.get("bulbs")
            state = parameters.get("state")
            if("all" in bulbs):
                socket_command += str(color_scheme["all"]) + " "
                if(state[0] == "on"):
                    socket_command += "111"
                else:
                    socket_command += "000"
            else:
                bulbs_dict = {}
                if(len(bulbs) == len(state)):
                    for i in range(len(bulbs)):
                        bulbs_dict[bulbs[i]] = state[i]
                else:
                    for i in range(len(bulbs)):
                        bulbs_dict[bulbs[i]] = state[0]
                for i in bulbs_dict:
                    if(i == "red green"):
                        bulbs_dict["red"] = bulbs_dict[i]
                        bulbs_dict["green"] = bulbs_dict[i]
                        del bulbs_dict["red green"]
                    elif(i == "red yellow"):
                        bulbs_dict["red"] = bulbs_dict[i]
                        bulbs_dict["yellow"] = bulbs_dict[i]
                        del bulbs_dict["red green"]
                    elif(i == "green yellow"):
                        bulbs_dict["green"] = bulbs_dict[i]
                        bulbs_dict["yellow"] = bulbs_dict[i]
                        del bulbs_dict["green yellow"]
                col = 0
                st = 8
                for i in bulbs_dict:
                    col += color_scheme[i]
                    if(i == "red" and bulbs_dict[i] == "on"):
                        st |= 4
                    elif(i == "green" and bulbs_dict[i] == "on"):
                        st |= 2
                    elif(i == "yellow" and bulbs_dict[i] == "on"):
                        st |= 1
                socket_command += str(col) + " "
                socket_command += str(bin(st)[3:])
                s.send(socket_command.encode())
                data = s.recv(1024)


                speech = data.decode()

                print("Response:")
                print(speech)

                return {
                    "speech": speech,
                    "displayText": speech,
                    #"data": {},
                    # "contextOut": [],
                    "source": "my_server"
                    }
    else:
        return {"speech": "I'm sorry! I cannot perform this action",
        "displayText": "I'm sorry! I cannot perform this action",
        #"data": {},
        # "contextOut": [],
        "source": "my_server"}

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port", str(port))



    app.run(debug=True, port=port, host="0.0.0.0")
