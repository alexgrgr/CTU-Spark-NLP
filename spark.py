#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
#                                 SPARKLIB                                     #
################################################################################

import json
import requests
import os

# Spark's header with Token defined in environmental variables
spark_header = {
        'Authorization': 'Bearer ' + os.environ.get('SPARK_ACCESS_TOKEN', None),
        'Content-Type': 'application/json; charset: utf-8'
        }

def get_displayName (personId):
    # To get the displayName of the user, Spark only needs to know the personId
    # or the personEmail
    message = requests.get(url='https://api.ciscospark.com/v1/people/'+personId,
                        headers=spark_header)
    JSON = message.json()
    return JSON.get("displayName")

def bot_answer(message, roomId):
    # This will generate a response to spark
    # [Debug]
    print ('Send to spark: \t'+ str(message))
    #Send in roomId received
    r = requests.post('https://api.ciscospark.com/v1/messages',
                 headers=spark_header, data=json.dumps({"roomId":roomId,
                                                      "markdown":message
                                                        }))
    print("Code after send_message POST: "+str(r.status_code))
    status= "Message sent to Spark"
    if r.status_code !=200:
        print(str(json.loads(r.text)))
        if   r.status_code == 403:
            status= "Oops, no soy moderador del team de dicha sala"
        elif r.status_code == 404:
            status= "Disculpe. Ya no soy miembro ni moderador de dicho grupo"
        elif r.status_code == 409:
            status= "Lo siento, no ha podido ser enviado (409)"
        elif r.status_code == 500:
            status= "Perdón, los servidores de Spark están sufriendo problemas.\
                               Compruébelo aquí: https://status.ciscospark.com/"
        elif r.status_code == 503:
            status= "Lo siento. Parece ser que los servidores de Spark no \
                                            pueden recibir mensajes ahora mismo"
        else:
            response = r.json()
            status= str('Error desconocido: \ '
                                         + response['errors'][0]['description'])
    return status
