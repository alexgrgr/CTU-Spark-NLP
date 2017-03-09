#CTU Spark and NLP integration example

## How to use a Spark Bot to answer a user´s *natural language* question with the ability to retreive data from external sources

This example shows how you can use a NLP (*Natural Language Procesor*), such as `Api.ai` to provide
information allocated at external sources or stored at the NLP database, in an easy way. This information and sources are described later in [`actions`](#actions).

###Use case

A user doesn´t want to use commands to ask for a Telepresence Device Datasheet, so the solution you need is an intermediate with some intelligence that could guess what the user is trying to ask in his human-like question.

Now, your bot will also be able to answer to spare questions so it will look more natural for the user to use it.

As before, possible sensitive data could be stored safely in your databases and in this example we will use *Smartsheet* again for storing the links to the products datasheets.

This new arquitecture looks like this:

![Architecture](docs/images/architecture.png)

Everything is deployed and integrated horizontally. Your app contains an interface for each integrated service.

![Connectors](docs/images/Connectors.png)

This example contains integrations of your app with *Spark*, *api.ai* and *Smartsheet*.

##Preparation Steps

1. **Create a new bot in Spark**

Please, create a new bot at [Documentation->Creating a Spark Bot](https://developer.ciscospark.com/bots.html#creating-a-spark-bot-account "Create Bot and Generate Access Token") and follow the steps.

 > Write down the access token

 2. **Prepare your Smartsheet's Token**

 As before, this data will be given to you.

 > Write down the access token for a later use.
 > Also, write down the sheet ID

3. **Set your agent at api.ai**

- **Upload intents**
+ Follow this link and download the zip file.
+ Create a new agent
+ Go to Setting->Impot and Export->Restore from zip
+ Select the zip you have just downloaded
- **Get Token**
+ Got to Settings->General and copy the *Client access token* under *API KEYS*
> Write down the access token for a later use
>
4. **Prepare a PaaS (*Platform as a Service*) for executing the code that will compose your bot.**

Again, follow this link to deploy the necessary code automatically on a Dyno:

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

You will be presented with a page as follow:

![New Heroku App](docs/images/newapp.JPG)

+ Select Your App name and save it for later use. Also referred as Dyno Name on this text.
+ Runtime selection, choose Europe
+ Now, set the *environmental variables*!:

![Variables](docs/images/newappvar.JPG)

|                Variable | Value                                                            |
|------------------------:|:-----------------------------------------------------------------|
| SMARTSHEET_ACCESS_TOKEN | Your *Smartsheet*´s Token to access *API*                        |
|                SHEET_ID | The *Smartsheet*'s sheet ID were info is located                 |
|      SPARK_ACCESS_TOKEN | Your bot´s Token to access *Spark* *API*                         |
|               BOT_EMAIL | Your bot´s email to discard its own messages                     |

+ Deploy!


4. **Set a WebHook to your Dyno in Spark**

Finally, link Spark with your app you will need to set a target where Spark will send all messages received by the bot. This is called a **Webhook**. Please refer to the following documentation:
 [*Spark WebHook Creation*](https://developer.ciscospark.com/endpoint-webhooks-post.html "Create an Spark Webhook").

You will notice on the left side of the above web the construction of the JSON message needed by Spark in order to contact it's API:

```JSON
{
  "name" : "My Awesome Webhook",
  "targetUrl" : "https://example.com/mywebhook",
  "resource" : "messages",
  "event" : "created",
  "filter" : "roomId=Y2lzY29zcGFyazovL3VzL1JPT00vYmJjZWIxYWQtNDNmMS0zYjU4LTkxNDctZjE0YmIwYzRkMTU0",
  "secret" : "86dacc007724d8ea666f88fc77d918dad9537a15"
}
```
Clicking on the scroll button you will change the mode to test mode. This allows a developer to send API messages directly from the web browser, instead of using a developer tool.

Your message needs to look this way:
```JSON
{
  "name" : "CTU Spark Commands Example",
  "targetUrl" : "https://[yourdynoname].herokuapp.com/webhook",
  "resource" : "messages",
  "event" : "created",
}
```
So you must set the following parameters:
+ **name**: `CTU Spark Commands Example`
+ **targetUrl**: where `[yourdynoname]` is the name given before to your Dyno
+ **resource**: `message`
+ **event**: `created`

> Now Spark knows where on the internet it must send the messages referred to your bot

##Ready

+ Any time your bot is referred in a Space, or chatted on a 1-to-1 Space, Spark will send a WebHook to `https://[yourdynoname].herokuapp.com/webhook`
+ Your Dyno is composed of some *Python* code over a web framework called *Flask*. Everytime a `GET` http request is received on the URL path `/webhook`, some code will be executed.
+ First of all, the WebHook does not include the message. Instead, a `messageId` is provided. So in order to have it, a `GET` http request is sent to Spark.
+ Then, the message `/search [something]` from a user will be decompossed into the command and the query.
+ This logic will be applied:

    **If `/search` exists, then search `[something]` in Smartsheet**

    **If `/search` does not exists, respond the user with the error**

+ End of the code, wait for next message.

## Deploy now:
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)


>In order to connect [*api.ai*](https://docs.api.ai/docs/webhook#section-step-4 "Create an api.ai webhook") webhook, URL is
`https://[yourappname].herokuapp.com/apiai`

>In order to connect [*Spark*](https://developer.ciscospark.com/endpoint-webhooks-post.html "Create an Spark Webhook") webhook, URL is
`https://[yourappname].herokuapp.com/webhook`

An intent with **webhook enabled** is needed, and the following values for `action`:<a id="actions"></a>

+ `search.smartsheet`: it will search for a query in *Smartsheet*. Just an example of *Smartsheet´s* potential.

+ `search.pam`: it will verify that the person asking is authorized to know that
data. Then, his/her PAM will be searched on Smartsheet. Finally, the bot will
announce on the group asked that it is a sensitive data and that it will tell
the employee in a 1-to-1 room. ***Not yet implemented***

+ `search.mypam`: same as `search.pam` but only to get owns PAM data. Partners will
be answered in a 1-to-1 room.

+ `search.am`: in this case, after a user verification, the account manager of a
given customer is retreived.
+`search.myam`: with a list of customers at smartsheet, it could tell him who is
his account manager.
+ `add.sparkclinic`: partner will be added to the room he asked to be in if the
list of rooms is added to the code. NLP processing used to get an exact ID.

**Note**: code for smartsheet is currently adapted to use specific Sheet IDs and
rows. This could change in a future to work with any ID.

###Environmental variables
You will also need to set this *environmental variables* in [*Heroku*](https://devcenter.heroku.com/articles/config-vars#setting-up-config-vars-for-a-deployed-application "Set Env variables"):

|                Variable | Value                                                            |
|------------------------:|:-----------------------------------------------------------------|
|      APIAI_ACCESS_TOKEN | Your *api.ai* client access Token                                |
|              APIAI_LANG | Processing language for api.ai. Default is *en*. Spanish is *es* |
|                APP_NAME | Your app´s name                                                  |
| SMARTSHEET_ACCESS_TOKEN | Your *Smartsheet*´s Token to access *API*                        |
|      SPARK_ACCESS_TOKEN | Your bot´s Token to access *Spark* *API*                         |
|               BOT_EMAIL | Your bot´s email to discard its own messages                     |

####How to get a *Token*

+ **Smartsheet**: follow steps in [Documentation](http://smartsheet-platform.github.io/api-docs/#generating-access-token "Generate Access Token")
+ **Spark**: follow steps in [Documentation->Creating a Spark Bot](https://developer.ciscospark.com/bots.html "Create Bot and Generate Access Token")
