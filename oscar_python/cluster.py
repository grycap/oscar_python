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

import oscar_python._utils as utils

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
    def get_info(self):
        return utils.make_request(self, _INFO_PATH, _GET)

    """ Function to get cluster config """
    def get_config(self):
        return utils.make_request(self, _CONFIG_PATH, _GET)
