#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
#                                  SDKLIB                                      #
# This file contains functions for interfacing other API's and internal tasks  #
################################################################################

import requests
import spark
import uuid
import time
import os

# Spark's header with Token defined in environmental variables
spark_header = {
        'Authorization': 'Bearer ' + os.environ.get('SPARK_ACCESS_TOKEN', None),
        'Content-Type': 'application/json'
        }

def get_user(req, sbuffer, user):
    # This will retrieve personID, personEmail and displayName
    #print("API.ai ID: \t" + str(req.get("sessionId")))
    #print(" Spark ID: \t" + str(sbuffer['sessionId']))
    #if str(req.get("id"))[15:] in str(sbuffer['sessionId']):
    user['personId']   = sbuffer['personId']
    user['personEmail']= sbuffer['personEmail']
    user['displayName']= sbuffer['displayName']
    found= True
    #                       \n   personId: \t" + user['personId']
    print("Message sent by: \n   personEmail: \t" + user['personEmail']
                          +"\n   displayName: \t" + user['displayName'])
    if not found: print ("Error, different sessionId")
    return found

def search (smartsheet, query):
    # The PAM of the specified user is searched or user's PAM. The sheet with
    # this information has sheetid= 6064162607523716
    sheetId = os.environ.get('SHEET_ID', None)
    # Now we search
    search_res = smartsheet.Search.search_sheet(sheetId, query)
    # Result is a smartsheet.models.SearchResult object.
    # Try - except for managing exceptions. If the following doesn´t
    # exists, we catch the exception, as it would mean we don´t have the
    # answer to the question
    try:
        rowId  = search_res.results[0].object_id
        # With the parameters needed to get the entire row, we request it
        row = smartsheet.Sheets.get_row(sheetId, rowId,
                    include='discussions,attachments,columns,columnType')
        # Answer is formatted in such a way that the cell where I know
        # where the data I want is in here:
        answer   = row.cells[1].value
        question = row.cells[0].value
    except:
        # If the before object doesn´t exists
        result = "Disculpe, no tenemos información de su pregunta " + query
    else:
        result = "El Datasheet del dispositivo **" + question + "** está [aquí]\
        ("+ answer +")"
    print("Para apiai/spark si se ha usado comando: " + result)
    return result

def buffer_it(JSON, sbuffer):
    # Webhook is triggered if a message is sent to the bot. The JSON and the
    # message unciphered are then saved
    # First step is to discard bot's own messages
    # First step is to discard bot's own messages
    if JSON['data']['personEmail'] != os.environ.get('BOT_EMAIL',
                                                                '@sparkbot.io'):
        roomId    = JSON['data']["roomId"]
        messageId = JSON['data']['id']
        # [Debug]
        #print("Message ID: \t" + messageId)

        # Message is not in the webhook. GET http request to Spark to obtain it
        message = requests.get(
                        url='https://api.ciscospark.com/v1/messages/'+messageId,
                    headers=spark_header)
        JSON = message.json()
        # Dictionary Containing info would be like this:
        # -------------------
        # |    sessionId    |  Identifies message at API.ai
        # !      roomId     |  Saving just in case
        # |message decrypted|  Used to compare with the message from api.ai
        # |    personId     |  Speaker unique ID
        # |   personEmail   |  Speaker unique email
        # |   displayName   |  Speaker´s displayed name
        # -------------------
        # Different ways of playing with JSON
        messagedecrypt  = JSON.get("text")
        personId        = JSON.get("personId")
        personEmail     = JSON.get("personEmail")
        # The Display Name of the person must be obtained from Spark too.
        # To get the displayName of the user, Spark only needs to know the
        # personId or the personEmail
        displayName = spark.get_displayName(personId)
        # [WARNING] UUIDV1 specifies string + time ID. Maybe there is need to use
        # roomId as identification, but not very well specified in Docs
        #sessionId = uuid.uuid1()
        # Session ID is based on roomId and Heroku URL
        sessionId = uuid.uuid5(uuid.NAMESPACE_DNS, str(roomId))
        # [Debug]
        #print ("Message Decrypted: "  + messagedecrypt
        #              + "\nroomId: \t"+ roomId
        #            + "\npersonId: \t"+ personId
        #          +"\npersonEmail: \t"+ personEmail
        #          +"\ndisplayName: \t"+ displayName
        #                 +"\nuuid: \t"+ str(sessionId))
        # Save all in buffer for clarification
        sbuffer['sessionId']  = str(sessionId)
        sbuffer['roomId']     = roomId
        sbuffer['message']    = messagedecrypt
        sbuffer['personId']   = personId
        sbuffer['personEmail']= personEmail
        sbuffer['displayName']= displayName
        return True
    else:
        print ("message from bot: ignoring")
        return False
