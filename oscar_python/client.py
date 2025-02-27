
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

import json
import os
import yaml
import liboidcagent as agent
import oscar_python._utils as utils
from oscar_python.default_client import DefaultClient
from oscar_python.storage import Storage

_INFO_PATH = "/system/info"
_CONFIG_PATH = "/system/config"
_SVC_PATH = "/system/services"
_LOGS_PATH = "/system/logs"
_RUN_PATH = "/run"
_STATUS_PATH="/system/status"


# _JOB_PATH = "/job"


_GET = "get"
_POST = "post"
_PUT = "put"
_DELETE = "delete"


class Client(DefaultClient):
    # Cluster info
    def __init__(self, options) -> None:
        self.set_auth_type(options)
        if self._AUTH_TYPE == 'basicauth':
            self.basic_auth_client(options)
        if self._AUTH_TYPE == 'oidc-agent':
            self.oidc_agent_client(options)
        if self._AUTH_TYPE == 'oidc':
            self.oidc_client(options)

    def basic_auth_client(self, options):
        self.id = options['cluster_id']
        self.endpoint = options['endpoint']
        self.user = options['user']
        self.password = options['password']
        self.ssl = bool(options['ssl'])

    def oidc_agent_client(self, options):
        self.id = options['cluster_id']
        self.endpoint = options['endpoint']
        self.shortname = options['shortname']
        self.ssl = bool(options['ssl'])

    def oidc_client(self, options):
        self.id = options['cluster_id']
        self.endpoint = options['endpoint']
        self.oidc_token = options['oidc_token']
        self.ssl = bool(options['ssl'])

    def set_auth_type(self, options):
        if 'user' in options:
            self._AUTH_TYPE = "basicauth"
        elif 'shortname' in options:
            self._AUTH_TYPE = "oidc-agent"
            try:
                agent.get_access_token(options['shortname'])
            except agent.OidcAgentError as e:
                print("ERROR oidc-agent: {}".format(e))
        elif 'oidc_token' in options:
            self._AUTH_TYPE = "oidc"
        else:
            raise ValueError("Unrecognized authentication credentials in options")

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

    def _check_fdl_definition(self, fdl_path):
        with open(fdl_path, "r") as read_fdl:
            fdl = self._parse_FDL_yaml(read_fdl)
        # Read FDL file and check correct format
        if fdl != ValueError:
            try:
                for element in fdl["functions"]["oscar"]:
                    try:
                        svc = element[self.id]
                    except KeyError as err:
                        raise Exception("FDL clusterID does not match current clusterID: {0}".format(err))
                    try:
                        with open(svc["script"]) as s:
                            svc["script"] = s.read()
                    except IOError:
                        raise Exception("Couldn't read script")

                    # cpu parameter has to be string on the request
                    if type(svc["cpu"]) is int or type(svc["cpu"]) is float: svc["cpu"] = str(svc["cpu"])

            except ValueError as err:
                print(err)
                raise
        else:
            raise ValueError("Bad yaml format: {0}".format(fdl))
        return svc

    """ Get status of a cluster (CPU and Memory) """
    def get_cluster_status(self):
        return utils.make_request(self, _STATUS_PATH, _GET)

    """ Make the request to create a new service """
    def _apply_service(self, svc, method):
        # Check if service already exists when the function is called from create_service
        if method == _POST:
            svc_exists = utils.make_request(self, _SVC_PATH+"/"+svc["name"], _GET, handle=False)
            if svc_exists.status_code == 200:
                raise ValueError("A service with name '{0}' is already present on the cluster".format(svc["name"]))
        return utils.make_request(self, _SVC_PATH, method, data=json.dumps(svc))

    """ Create a service on the current cluster from a FDL file or a JSON definition """
    def create_service(self, service_definition):
        if type(service_definition) is dict:
            return self._apply_service(service_definition, _POST)
        if os.path.isfile(service_definition):
            service = self._check_fdl_definition(service_definition)
            return self._apply_service(service, _POST)
        raise ValueError("Service definition must be a dictionary or a file path")

    """ Update a specific service from a FDL file or a JSON definition """
    def update_service(self, name, new_service):
        # Check if service exists before update
        svc = utils.make_request(self, _SVC_PATH+"/"+name, _GET, handle=False)
        if svc.status_code != 200:
            raise ValueError("The service {0} is not present on the cluster".format(name))
        if type(new_service) is dict:
            return self._apply_service(new_service, _PUT)
        if os.path.isfile(new_service):
            try:
                service = self._check_fdl_definition(new_service)
            except Exception:
                raise
            return self._apply_service(service, _PUT)

    """ Remove a specific service """
    def remove_service(self, name):
        return utils.make_request(self, _SVC_PATH+"/"+name, _DELETE)

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
