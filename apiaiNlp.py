#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
#                                    apiai                                     #
# SDK for api.ai                                                               #
################################################################################

import json
import apiai
import requests
import os


def apiai_send (ai, sbuffer, abuffer):
    # Prepares and sends message to apiai the response is returned as-is
    request = ai.text_request()
    request.lang = os.environ.get('APIAI_LANG', 'es')  # optional, default value
    # equal 'en' Session ID has been generated before and storaged on array
    #print ("Setting sessionId: "+ sbuffer['sessionId'])
    request.session_id = sbuffer['sessionId']
    #print("Setting message: "+ sbuffer['message'])
    request.query = sbuffer['message']
    response = json.loads(request.getresponse().read().decode('UTF-8'))
    #print (response)
    abuffer['message']   = response['result']['fulfillment']['speech']
    abuffer['confident'] = response['result']['score']
    abuffer['sessionId'] = response['sessionId']
    abuffer['action']    = response['result']['action']
    print ("Confident: \t"+ str(abuffer['confident'])
       + "\nsessionId: \t"+ str(abuffer['sessionId'])
          + "\nAction: \t"+ str(abuffer['action']))
    status = True
    return status

def apiai2spark (abuffer, sbuffer):
    # Prepare message to send back to Spark
    #print ("Converting from apiai to Spark format...")
    sbuffer['message'] = str(abuffer['message'])
    return True
