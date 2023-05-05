
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

import os
import json
import yaml
import oscar_python._utils as utils
from oscar_python.storage import Storage

_INFO_PATH = "/system/info"
_CONFIG_PATH = "/system/config"
_SVC_PATH = "/system/services"
_LOGS_PATH = "/system/logs"
_RUN_PATH = "/run"
#_JOB_PATH = "/job"

_MINIO = "minio"
_S3 = "s3"
_ONE_DATA = "onedata"
_WEBDAV = "webdav"

_GET = "get"
_POST = "post"
_PUT = "put"
_DELETE = "delete"
_DEFAULT_TIMEOUT = 30

class Client:
    #Cluster info 
    def __init__(self, id, endpoint, user, password, ssl) -> None:
        self.id = id
        self.endpoint = endpoint
        self.user = user
        self.password = password
        self.ssl = ssl

    """ Creates a generic storage client to interact with the storage providers 
    defined on a specific service of the refered OSCAR cluster """
    def create_storage_client(self, svc):
        return Storage(
                client_obj=self,
                svc_name=svc)

    """ Function to get cluster info """
    def get_cluster_info(self):
        return utils.make_request(self, _INFO_PATH, _GET)

    """ Function to get cluster config """
    def get_cluster_config(self):
        return utils.make_request(self, _CONFIG_PATH, _GET)

    """ List all services from the current cluster """
    def list_services(self):
        return utils.make_request(self, _SVC_PATH, _GET)
    
    """ Retreive a specific service """
    def get_service(self, name):
        return utils.make_request(self, _SVC_PATH+"/"+name, _GET)

    def _apply_service(self, fdl_path, method):
        with open(fdl_path, "r") as read_fdl:
            fdl = self._parse_FDL_yaml(read_fdl)
        # Read FDL file and check correct format
        if fdl != ValueError:
            for element in fdl["functions"]["oscar"]:
                try:
                    svc = element[self.id]
                except KeyError as err:
                    raise("FDL clusterID does not match current clusterID: {0}".format(err))
                # Check if service already exists when the function is called from create_service
                if method == _POST:
                    svc_exists = utils.make_request(self, _SVC_PATH+"/"+svc["name"], _GET, handle=False)
                    if svc_exists.status_code == 200:
                        raise ValueError("A service with name '{0}' is already present on the cluster".format(svc["name"]))
                try:
                    with open(svc["script"]) as s:
                        svc["script"] = s.read()
                except IOError as err:
                    raise("Couldn't read script")

                # cpu parameter has to be string on the request
                if type(svc["cpu"]) is int or type(svc["cpu"]) is float: svc["cpu"]= str(svc["cpu"])
                utils.make_request(self, _SVC_PATH, method, data=json.dumps(svc))
        else:
            raise ValueError("Bad yaml format: {0}".format(fdl))

    """ Create a service on the current cluster from a FDL file """
    def create_service(self, fdl_path):
        return self._apply_service(fdl_path, _POST)

    """ Update a specific service """
    def update_service(self, name, fdl_path):
        # Check if service exists before update
        svc = utils.make_request(self, _SVC_PATH+"/"+svc["name"], _GET, handle=False)
        if svc.status_code != 200:
            raise ValueError("The service {0} is not present on the cluster".format(name))
        return self._apply_service(fdl_path, _PUT)

    """ Remove a specific service """
    def remove_service(self, name):
        return utils.make_request(self, _SVC_PATH+"/"+name, _DELETE)

    """ Run a synchronous execution. 
        If an output is provided the result is decoded onto the file.
        In both cases the function returns the HTTP response."""
    def run_service(self, name, **kwargs):
        if "input" in kwargs.keys() and kwargs["input"]:
            exec_input = kwargs["input"]
            token = self._get_token(name) 
            
            send_data = utils.encode_input(exec_input)

            if "timeout" in kwargs.keys() and kwargs["timeout"]:
                response = utils.make_request(self, _RUN_PATH+"/"+name, _POST, data=send_data, token=token, timeout=kwargs["timeout"])
            else:
                response = utils.make_request(self, _RUN_PATH+"/"+name, _POST, data=send_data, token=token)
            
            if "output" in kwargs.keys() and kwargs["output"]:
                utils.decode_output(response.text, kwargs["output"])
            return response
        
        return utils.make_request(self, _RUN_PATH+"/"+name, _POST, token=token)
    
    """ Run an asynchronous execution (unable at the moment). """
    #TODO
    """ def _run_job(self, name, input_path =""):
            pass 
    """

    def _get_token(self, svc):
        service = utils.make_request(self, _SVC_PATH+"/"+svc, _GET)
        service = json.loads(service.text)
        return service["token"]

    def _parse_FDL_yaml(self, fdl_read_pointer):
        try:
            fdl_yaml = yaml.safe_load(fdl_read_pointer)
        except ValueError as err:
            return err
        return fdl_yaml
    
    """ Get logs of a service job """
    def get_job_logs(self, svc, job):
        return utils.make_request(self, _LOGS_PATH+"/"+svc+"/"+job, _GET)
    
    """ List a service jobs """
    def list_jobs(self, svc):
        return utils.make_request(self, _LOGS_PATH+"/"+svc, _GET)

    """ Remove a service job """
    def remove_job(self, svc, job):
        return utils.make_request(self, _LOGS_PATH+"/"+svc+"/"+job, _DELETE)

    """ Remove all service jobs """
    def remove_all_jobs(self, svc):
        return utils.make_request(self, _LOGS_PATH+"/"+svc, _DELETE)
