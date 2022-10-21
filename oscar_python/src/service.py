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

from cluster import Cluster
import _utils as utils
import json
import yaml

_SVC_PATH = "/system/services"
_RUN_PATH = "/run"
_JOB_PATH = "/job"
_GET = "get"
_POST = "post"
_PUT = "put"
_DELETE = "delete"

class Service:
    def __init__(self, cluster: Cluster) -> None:
        self.cluster = cluster

    """ List all services from the current cluster """
    def list_services(self):
        return utils.make_request(self.cluster, _SVC_PATH, _GET)
    
    """ Retreive a specific service """
    def get_service(self, name):
        return utils.make_request(self.cluster, _SVC_PATH+"/"+name, _GET)

    def _apply_service(self, fdl_path, method):
        with open(fdl_path, "r") as read_fdl:
            fdl = self._parse_FDL_yaml(read_fdl)
        if fdl != ValueError:
            for element in fdl["functions"]["oscar"]:
                try:
                    svc = element[self.cluster.id]
                except KeyError as err:
                    print("Error: FDL clusterID don't match current clusterID: {0}".format(err))
                    return err
                try:
                    with open(svc["script"]) as s:
                        svc["script"] = s.read()
                except IOError as err:
                    print("Error: Couldn't read script")
                    return err

                # cpu parameter has to be string on the request
                if type(svc["cpu"]) is int or type(svc["cpu"]) is float: svc["cpu"]= str(svc["cpu"])
                return utils.make_request(self.cluster, _SVC_PATH, method, json.dumps(svc))
        else:
            print("Error: Bad yaml format: {0}".format(fdl))
            return ValueError

    """ Create a service on the current cluster from a FDL file """
    def create_service(self, fdl_path):
        self._apply_service(fdl_path, _POST)

    """ Update a specific service """
    def update_service(self, name, fdl_path):
        svc = self.get_service(name)
        if svc.status_code != 200:
            print("Error: the service {0} is not present on the cluster".format(name))
            return
        self._apply_service(fdl_path, _PUT)

    """ Remove a specific service """
    def remove_service(self, name):
        return utils.make_request(self.cluster, _SVC_PATH+"/"+name, _DELETE)

    """ Run a synchronous execution """
    def run_service(self, name, input=""):
        token = self._get_token(name)
        if input: return utils.make_request(self.cluster, _RUN_PATH+"/"+name, _POST, input=input, token=token)
        return utils.make_request(self.cluster, _RUN_PATH+"/"+name, _POST, token=token)
    
    """ Run an asynchronous execution (not usable at the moment). """
    #TODO fix
    def _run_job(self, name, input_path =""):
        token = self._get_token(name)
        if input:
            files = {'input': open(input_path, "rb")}
            return utils.make_request(self.cluster, "/job/"+name, _POST, file=files, token=token)
        return utils.make_request(self.cluster, "job/"+name, _POST, token=token)

    def _get_token(self, svc):
        service = utils.make_request(self.cluster, _SVC_PATH+"/"+svc, _GET)
        service = json.loads(service.text)
        return service["token"]

    def _parse_FDL_yaml(self, fdl_read_pointer):
        try:
            fdl_yaml = yaml.safe_load(fdl_read_pointer)
        except ValueError as err:
            return err
        return fdl_yaml