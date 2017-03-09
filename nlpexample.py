#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
#                                 ALICEBOT                                     #
#               https://yourappname.herokuapp.com:443/apiai                    #
#               https://yurappname.herokuapp.com:443/webhook                   #
# Flow:                                                                        #
# Spark--------------                                                          #
#                   |                                                          #
#                   ------>nlpexample/webhook                                  #
#                    if command found----> External Sources:                   #
#                                                           smartsheet,        #
#                                                           PacoApp,           #
#                                                           Spark,...          #
#                                                             |                #
#                                       -----------------------                #
#                                       |                                      #
#                        nlpexample<-----                                      #
# Spark<----------------------|                                                #
#                                                                              #
#                                                                              #
#                       if no command----                                      #
#                                       |                                      #
#                                       ----------------------> NLP            #
#                                                                 |            #
#                                       --------------------------             #
#                                       |                                      #
#                        nlpexample<----                                       #
#                      if no action                                            #
# Spark<----------------------|                                                #
#                      if actions--------> External Sources:                   #
#                                                           smartsheet,        #
#                                                           PacoApp,           #
#                                                           Spark,...          #
#                                                             |                #
#                                       -----------------------                #
#                                       |                                      #
#                        nlpexample<-----                                      #
#                          |                                                   #
#                          -------------------------------------> NLP          #
#                                                                 |            #
#                                       --------------------------             #
#                                       |                                      #
# Spark<-----------------Alice<---------                                       #
################################################################################

# Note that this time the following code has been divided in different files
# to make a clearer code.

# Disclaimer: Don´t use this code as a best practices example, as it has not
# been verified as the best way of coding Python. Refer to
# https://www.python.org/ for reliable documentation.

import smartsheet
import json
import os
import apiai

import sdk
import spark
import apiaiNlp

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)

# Instantiation of APIai object.
ai = apiai.ApiAI(os.environ.get('APIAI_ACCESS_TOKEN', None))

# Instantiation of Smartsheet object
smartsheet = smartsheet.Smartsheet()

# Buffer for capturing messages from Spark
sbuffer = {"sessionId":"","roomId":"","message":"",
           "personId":"","personEmail":"","displayName":""}
# Buffer for capturing messages from api.ai
abuffer = {"sessionId":"","confident":"", "message":"","action":"",
                                "parameters":""}
# Defining user's dict
user    = {"personId":"","personEmail":"","displayName":""}

# Message Received from Spark
@app.route('/webhook', methods=['POST','GET'])
def webhook():
    # Every message from Spark is received here. I will be analyzed and sent to
    # api.ai response will then sent back to Spark
    req = request.get_json(silent=True, force=True)
    res = spark_webhook(req)
    return None

@app.route('/apiai', methods=['POST','GET'])
def apiai():
    # If there is external data to retrieve, APIai will send a WebHook here
    req = request.get_json(silent=True, force=True)
    # [Debug]
    print("[API.ai] There is an action: "+req["result"]["action"])
    res = apiai_webhook(req)
    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r





def spark_webhook (req):
    # JSON is from Spark. This will contain the message, a personId, displayName,
    # and a personEmail that will be buffered for future use.
    # This time, code has been splitted in different parts for clarity
    # The next function is contained at the sdk file on the same path
    # as this main code.
    if sdk.buffer_it(req, sbuffer):
        # If a command is identified, you don´t need to ask to api.ai
        if "/search" in sbuffer["message"]:
            query = sbuffer["message"].replace('/search', '')
            #[debug]
            print ("Asked to search " + query)
            # Also, the answer will overwrite the question in the buffer
            sbuffer['message'] = sdk.search (smartsheet, query)
            print(sbuffer["message"])
            status = "Search OK"
        else:
            # If we cannot guess any command, then we will use api.ai to
            # identify the question. Once this is done, we need to prepare and
            # send the message for APIai
            done = apiaiNlp.apiai_send (ai, sbuffer, abuffer)
            if done:
                apiaiNlp.apiai2spark(abuffer, sbuffer)
                #status = spark.bot_answer(
                #                    sbuffer['message'],
                #                    sbuffer['roomId'])
            else:
                status = "apiai does not know the answer"
                #spark.bot_answer(
                #            "Ups, apiai no ha asociado su pregunta a ningún \
                #            intent",
                #            sbuffer['roomId'])
                sbuffer["message"] = "Ups, apiai no ha asociado su pregunta a \
                ningún intent"
        spark.bot_answer(
                    sbuffer["message"],
                    sbuffer['roomId'])
    else:
        status = "Error buffering or message from bot"
    return status


def apiai_webhook(req):
    # JSON is from api.ai. This will contain the message, the action and the
    # parameters
    print ("Parameters: "+str(req.get("result").get("parameters")))
    # api.ai request to search for a datasheet
    action = req.get("result").get("action")
    if  action == 'search.query':
        if sdk.get_user(req, sbuffer, user):
            query = req.get("result").get("parameters").get("query")
            string_res = sdk.search(smartsheet, query)
        else:
            string_res="Fallo en la obtención del usuario desde Spark. Pruebe \
                        de nuevo, por favor."
    else:
        # If the action is different from the aboves, you answer this
        string_res = "Ooops, se ha confundido con el **action**\n\t \
                    Action: " + str(action) + ", y deberia ser search.query"
    return{
        # This is the JSON structure apiai is expecting
        "speech": str(string_res),
        "displayText": str(string_res),
        "source": "nlpexample.py"
        }

# App is listening to webhooks. Next line is used to executed code only if it is
# running as a script, and not as a module of another script.
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, port=port, host='0.0.0.0', threaded=True)
