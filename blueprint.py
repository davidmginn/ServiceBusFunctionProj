# Register this blueprint by adding the following line of code 
# to your entry point file.  
# app.register_functions(blueprint) 
# 
# Please refer to https://aka.ms/azure-functions-python-blueprints


import azure.functions as func
import logging
from azure.servicebus import ServiceBusClient, ServiceBusMessage
import os
import json

blueprint = func.Blueprint()


@blueprint.route(route="http_trigger", auth_level=func.AuthLevel.FUNCTION)
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    connstr = os.environ['ServiceBusConnectionString']
    queue_name = "demo"

    #create a list of 100 ServieBusMessages
    messages = []

    #create 100 metadata objects of 100 lines each and add them to the messages array
    for i in range(100):
        metadata = Metadata(i*100, (i+1)*100)
        json_metadata = json.dumps(metadata.__dict__)
        messages.append(ServiceBusMessage(json_metadata))

    with ServiceBusClient.from_connection_string(connstr) as client:
        with client.get_queue_sender(queue_name) as sender:
            sender.send_messages(messages)

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )


@blueprint.service_bus_queue_trigger(arg_name="azservicebus", queue_name="demo",
                               connection="ServiceBusConnectionString") 
def servicebus_trigger(azservicebus: func.ServiceBusMessage):
    #deserialize the message body into a metadata object
    metadata = json.loads(azservicebus.get_body().decode('utf-8'))
    #log the start and end line numbers
    logging.info("Start line: %s", metadata["start"])
    logging.info("End line: %s", metadata["end"])


#define a class with integer properties for start and end line
class Metadata:
    def __init__(self, start, end):
        self.start = start
        self.end = end