
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
from oscar_python._oidc import OIDC
from oscar_python.default_client import DefaultClient
from oscar_python.storage import Storage

_INFO_PATH = "/system/info"
_CONFIG_PATH = "/system/config"
_SVC_PATH = "/system/services"
_LOGS_PATH = "/system/logs"
_RUN_PATH = "/run"
_STATUS_PATH = "/system/status"
_HEALTH_PATH = "/health"
_VOLUMES_PATH = "/system/volumes"
_BUCKETS_PATH = "/system/buckets"
_METRICS_PATH = "/system/metrics"
_QUOTAS_USER_PATH = "/system/quotas/user"
_FEDERATION_PATH = "/system/federation"


# _JOB_PATH = "/job"


_GET = "get"
_POST = "post"
_PUT = "put"
_DELETE = "delete"

# Default values for OIDC refresh token using EGI CheckIn
_DEFAULT_SCOPES = ['openid', 'email', 'profile', 'voperson_id', 'eduperson_entitlement']
_DEFAULT_TOKEN_ENDPOINT = 'https://aai.egi.eu/auth/realms/egi/protocol/openid-connect/token'
_DEFAULT_CLIENT_ID = 'token-portal'


class Client(DefaultClient):
    # Cluster info
    def __init__(self, options) -> None:
        self.id = options['cluster_id']
        self.endpoint = options['endpoint']
        self.set_auth_type(options)
        if self._AUTH_TYPE == 'basicauth':
            self.basic_auth_client(options)
        if self._AUTH_TYPE == 'oidc-agent':
            self.oidc_agent_client(options)
        if self._AUTH_TYPE == 'oidc':
            self.oidc_client(options)

    def basic_auth_client(self, options):
        self.user = options['user']
        self.password = options['password']
        self.ssl = bool(options['ssl'])

    def oidc_agent_client(self, options):
        self.shortname = options['shortname']
        self.ssl = bool(options['ssl'])

    def oidc_client(self, options):
        self.oidc_token = options.get('oidc_token')
        self.refresh_token = options.get('refresh_token')
        self.scopes = options.get('scopes', _DEFAULT_SCOPES)
        self.token_endpoint = options.get('token_endpoint',
                                          _DEFAULT_TOKEN_ENDPOINT)
        self.ssl = bool(options['ssl'])
        self.client_id = options.get('client_id',
                                     _DEFAULT_CLIENT_ID)

    def set_auth_type(self, options):
        if 'user' in options:
            self._AUTH_TYPE = "basicauth"
        elif 'shortname' in options:
            self._AUTH_TYPE = "oidc-agent"
            try:
                agent.get_access_token(options['shortname'])
            except agent.OidcAgentError as e:
                print("ERROR oidc-agent: {}".format(e))
        elif 'oidc_token' in options or 'refresh_token' in options:
            self._AUTH_TYPE = "oidc"
        else:
            raise ValueError("Unrecognized authentication credentials in options")

    def get_access_token(self):
        if self.refresh_token and OIDC.is_access_token_expired(self.oidc_token):
            self.oidc_token = OIDC.refresh_access_token(self.refresh_token,
                                                        self.scopes,
                                                        self.token_endpoint,
                                                        self.client_id)
        return self.oidc_token

    """ Creates a generic storage client to interact with the storage providers
    defined on a specific service of the refered OSCAR cluster """
    def create_storage_client(self, svc=None):
        if svc is not None:
            return Storage(
                client_obj=self, svc_name=svc)
        else:
            return Storage(
                    client_obj=self)

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
                        if os.path.isabs(svc["script"]):
                            script_path = svc["script"]
                        else:
                            fdl_directory = os.path.dirname(fdl_path)
                            script_path = os.path.join(fdl_directory, svc['script'])
                        with open(script_path) as s:
                            svc["script"] = s.read()
                    except IOError:
                        raise Exception("Couldn't read script")

                    # cpu parameter has to be string on the request
                    if type(svc["cpu"]) is int or type(svc["cpu"]) is float:
                        svc["cpu"] = str(svc["cpu"])

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
        if self._AUTH_TYPE != 'basicauth':
            return self.get_access_token()
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
    def list_jobs(self, svc, page=""):
        return utils.make_request(self, _LOGS_PATH+"/"+svc+"?page="+page, _GET)

    """ Remove a service job """
    def remove_job(self, svc, job):
        return utils.make_request(self, _LOGS_PATH+"/"+svc+"/"+job, _DELETE)

    """ Remove all service jobs """
    def remove_all_jobs(self, svc):
        return utils.make_request(self, _LOGS_PATH+"/"+svc, _DELETE)

    """ Check cluster health """
    def health_check(self):
        return utils.make_request(self, _HEALTH_PATH, _GET)

    """ Get deployment status of a service """
    def get_deployment_status(self, name):
        return utils.make_request(self, _SVC_PATH + "/" + name + "/deployment", _GET)

    """ Get deployment logs of a service """
    def get_deployment_logs(self, name):
        return utils.make_request(self, _SVC_PATH + "/" + name + "/deployment/logs", _GET)

    """ List all managed volumes """
    def list_volumes(self):
        return utils.make_request(self, _VOLUMES_PATH, _GET)

    """ Create a new managed volume """
    def create_volume(self, name, size):
        data = json.dumps({"name": name, "size": size})
        return utils.make_request(self, _VOLUMES_PATH, _POST, data=data)

    """ Get a specific managed volume """
    def get_volume(self, name):
        return utils.make_request(self, _VOLUMES_PATH + "/" + name, _GET)

    """ Delete a managed volume """
    def delete_volume(self, name):
        return utils.make_request(self, _VOLUMES_PATH + "/" + name, _DELETE)

    """ Create a bucket """
    def create_bucket(self, name, visibility="private", allowed_users=None):
        data = json.dumps({
            "bucket_name": name,
            "visibility": visibility,
            "allowed_users": allowed_users or []
        })
        return utils.make_request(self, _BUCKETS_PATH, _POST, data=data)

    """ Update a bucket """
    def update_bucket(self, name, visibility, allowed_users=None):
        data = json.dumps({
            "bucket_name": name,
            "visibility": visibility,
            "allowed_users": allowed_users or []
        })
        return utils.make_request(self, _BUCKETS_PATH, _PUT, data=data)

    """ List all buckets """
    def list_buckets(self):
        return utils.make_request(self, _BUCKETS_PATH, _GET)

    """ Get a specific bucket """
    def get_bucket(self, name):
        return utils.make_request(self, _BUCKETS_PATH + "/" + name, _GET)

    """ Delete a bucket """
    def delete_bucket(self, name):
        return utils.make_request(self, _BUCKETS_PATH + "/" + name, _DELETE)

    """ Get a presigned URL for a bucket file """
    def presign_bucket(self, name, object_key, operation="download", expires=0, content_type="", extra_headers=None):
        path = _BUCKETS_PATH + "/" + name + "/presign"
        data = json.dumps({
            "object_key": object_key,
            "operation": operation,
            "expires": expires,
            "content_type": content_type,
            "extra_headers": extra_headers or {},
        })
        return utils.make_request(self, path, _POST, data=data)

    """ Get system logs (admin only) """
    def get_system_logs(self, timestamps=False, previous=False):
        path = _LOGS_PATH
        params = []
        if timestamps:
            params.append("timestamps=true")
        if previous:
            params.append("previous=true")
        if params:
            path += "?" + "&".join(params)
        return utils.make_request(self, path, _GET)

    """ Get metrics summary """
    def get_metrics_summary(self):
        return utils.make_request(self, _METRICS_PATH, _GET)

    """ Get metrics breakdown """
    def get_metrics_breakdown(self, group_by="service"):
        return utils.make_request(self, _METRICS_PATH + "/breakdown?group_by=" + group_by, _GET)

    """ Get metrics for a specific service """
    def get_service_metrics(self, service_name):
        return utils.make_request(self, _METRICS_PATH + "/" + service_name, _GET)

    """ Get own quota """
    def get_own_quota(self):
        return utils.make_request(self, _QUOTAS_USER_PATH, _GET)

    """ Get quota for a specific user """
    def get_user_quota(self, user_id):
        return utils.make_request(self, _QUOTAS_USER_PATH + "/" + user_id, _GET)

    """ Update quota for a user """
    def update_user_quota(self, user_id, cpu, memory):
        data = json.dumps({"cpu": cpu, "memory": memory})
        return utils.make_request(self, _QUOTAS_USER_PATH + "/" + user_id, _PUT, data=data)

    """ Get federation members for a service """
    def get_federation(self, service_name):
        return utils.make_request(self, _FEDERATION_PATH + "/" + service_name, _GET)

    """ Add federation members to a service """
    def add_federation_members(self, service_name, members, clusters=None, storage_providers=None):
        data = {"members": members}
        if clusters:
            data["clusters"] = clusters
        if storage_providers:
            data["storage_providers"] = storage_providers
        return utils.make_request(self, _FEDERATION_PATH + "/" + service_name, _POST, data=json.dumps(data))

    """ Update federation members of a service """
    def update_federation_members(self, service_name, members, update, clusters=None, storage_providers=None):
        data = {"members": members, "update": update}
        if clusters:
            data["clusters"] = clusters
        if storage_providers:
            data["storage_providers"] = storage_providers
        return utils.make_request(self, _FEDERATION_PATH + "/" + service_name, _PUT, data=json.dumps(data))

    """ Remove federation members from a service """
    def remove_federation_members(self, service_name, members, delete=False):
        data = {"members": members, "delete": delete}
        return utils.make_request(self, _FEDERATION_PATH + "/" + service_name, _DELETE, data=json.dumps(data))
