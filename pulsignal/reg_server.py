import requests
import logging

def register_server(configuration):
    response=requests.post("http://" + configuration.get_server_address() + "/api/register/"+configuration.get_client_key())
    return response.json()["auth_key"]
