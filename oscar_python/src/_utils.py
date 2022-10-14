import base64
import requests
from rsa import verify

""" Generic http request """
def makeRequest(c , path, method, data="", token=""):
    url = c.endpoint+path
    headers = getHeaders(c)
    if method == "post" or "put":
        if token: headers = getHeadersWithToken(token)
        if data: return requests.request(method, url, headers=headers, verify=c.ssl, data=data)
    return requests.request(method, url, headers=headers)

""" Function to generate headers with basic authentication """
def getHeaders(c):
    usr_pass_as_bytes = bytes(c.user+":"+c.password,"utf-8")
    usr_pass_base_64 = base64.b64encode(usr_pass_as_bytes).decode("utf-8")
    return {"Authorization": "Basic "+ usr_pass_base_64}

""" Function to generate headers with token auth """
def getHeadersWithToken(token):
    return {"Authorization": "Bearer "+ str(token)}