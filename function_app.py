import azure.functions as func
import logging
from blueprint import blueprint

app = func.FunctionApp()

app.register_functions(blueprint)