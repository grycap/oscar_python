import base64
import requests

""" Generic http request """
def make_request(c , path, method, data="", file="", token=""):
    url = c.endpoint+path
    headers = get_headers(c)
    if method == "post" or "put":
        if token: headers = get_headers_with_token(token)
        if data: return requests.request(method, url, headers=headers, verify=c.ssl, data=data)
        if file: return requests.request(method, url, headers=headers, verify=c.ssl, files=file)
    return requests.request(method, url, headers=headers)

""" Function to generate headers with basic authentication """
def get_headers(c):
    usr_pass_as_bytes = bytes(c.user+":"+c.password,"utf-8")
    usr_pass_base_64 = base64.b64encode(usr_pass_as_bytes).decode("utf-8")
    return {"Authorization": "Basic "+ usr_pass_base_64}

""" Function to generate headers with token auth """
def get_headers_with_token(token):
    return {"Authorization": "Bearer "+ str(token)}