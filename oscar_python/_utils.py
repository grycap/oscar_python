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
import os
import requests
import liboidcagent as agent
_DEFAULT_TIMEOUT = 60


def make_request(c, path, method, **kwargs):
    """ Generic http request """

    headers = get_headers(c)

    if "timeout" in kwargs.keys() and kwargs["timeout"]:
        timeout = kwargs["timeout"]
    else:
        timeout = _DEFAULT_TIMEOUT

    url = c.endpoint+path

    if method in ["post", "put"]:
        if "token" in kwargs.keys() and kwargs["token"]: 
            headers = get_headers_with_token(kwargs["token"])
        if "data" in kwargs.keys() and kwargs["data"]:
            result = requests.request(method, url, headers=headers, verify=c.ssl, data=kwargs["data"], timeout=timeout)
    else:
        result = requests.request(method, url, headers=headers, verify=c.ssl, timeout=timeout)

    if "handle" in kwargs.keys() and kwargs["handle"] == False:
        return result

    result.raise_for_status()
    return result


def get_headers(c):
    """ Function to generate headers with basic authentication or OIDC """
    if c._AUTH_TYPE == "basicauth":
        usr_pass_as_bytes = bytes(c.user + ":" + c.password, "utf-8")
        usr_pass_base_64 = base64.b64encode(usr_pass_as_bytes).decode("utf-8")
        return {"Authorization": "Basic " + usr_pass_base_64}
    if c._AUTH_TYPE == "oidc-agent":
        token = agent.get_access_token(c.shortname)
        return get_headers_with_token(token)
    if c._AUTH_TYPE == "oidc":
        return get_headers_with_token(c.oidc_token)


def get_headers_with_token(token):
    """ Function to generate headers with token auth """
    return {"Authorization": "Bearer " + str(token)}


def write_text_file(content, file_path):
    with open(file_path, 'w') as f:
        f.write(content)


def isBase64(st):
    try:
        base64.b64decode(st)
        return True
    except Exception:
        return False


def decode_b64(b64_str, file_out):
    file_extension = os.path.splitext(file_out)[1]
    try:
        decoded_data = base64.b64decode(b64_str)

        if file_extension in [".txt", ".json"]:
            decode = 'w'
            decoded_data = decoded_data.decode("utf-8")
        else:
            decode = 'wb'

        with open(file_out, decode) as f:
            f.write(decoded_data)

    except ValueError:
        print('Error decoding output: Invalid base64 string.')
    except OSError:
        print('Error decoding output: Failed to write decoded data to file.')   


def encode_input(data):
    if os.path.isfile(data):
        try:
            with open(data, 'rb') as file:
                return base64.b64encode(file.read())
        except FileNotFoundError:
            print('Error encoding input: File {0} not found.'.format(data))
        except OSError:
            print('Error encoding input: Failed to read file.')
    else:
        message_bytes = data.encode('ascii')
        return base64.b64encode(message_bytes)


def decode_output(output, file_path):
    if isBase64(output):
        decode_b64(output, file_path)
        return
    if isinstance(output, str):
        write_text_file(output, file_path)
        return
