# Copyright (C) GRyCAP - I3M - UPV

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License. 

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