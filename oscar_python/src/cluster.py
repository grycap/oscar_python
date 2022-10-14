import base64
import requests
import _utils as utils
from rsa import verify

_INFO_PATH = "/system/info"
_CONFIG_PATH = "/system/config"
_GET = "get"
class Cluster:
    def __init__(self, id, endpoint, user, password, ssl) -> None:
        self.id = id
        self.endpoint = endpoint
        self.user = user
        self.password = password
        self.ssl = ssl

    """ Function to get cluster info """
    def getInfo(self):
        return utils.makeRequest(self, _INFO_PATH, _GET)

    """ Function to get cluster config """
    def getConfig(self):
        return utils.makeRequest(self, _CONFIG_PATH, _GET)
