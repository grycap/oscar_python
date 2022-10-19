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

    """ Create a service on the current cluster from a FDL file """
    def create_service(self, fdl_path):
        with open(fdl_path, "r") as read_fdl:
            fdl = self._parse_FDL_yaml(read_fdl)
        if fdl != ValueError:
            for element in fdl["functions"]["oscar"]:
                try:
                    svc = element[self.cluster.id]
                except KeyError as err:
                    print("Error: FDL clusterID don't match current clusterID: {0}".format(err))
                    exit()
                try:
                    with open(svc["script"]) as s:
                        svc["script"] = s.read()
                except IOError as err:
                    print("Error: Couldn't read script")
                    exit()

                # cpu parameter has to be string on the request
                if type(svc["cpu"]) is int or type(svc["cpu"]) is float: svc["cpu"]= str(svc["cpu"])
                return utils.make_request(self.cluster, _SVC_PATH, _POST, json.dumps(svc))
        else:
            print("Error: Bad yaml format: {0}".format(fdl))

    """ Update a specific service """
    def update_service(self, name):
        pass

    """ Remove a specific service """
    def remove_service(self, name):
        return utils.make_request(self.cluster, _SVC_PATH+"/"+name, _DELETE)

    """ Run a synchronous execution """
    def run_service(self, name, input=""):
        token = self._get_token(name)
        if input: return utils.make_request(self.cluster, _RUN_PATH+"/"+name, _POST, input=input, token=token)
        return utils.make_request(self.cluster, _RUN_PATH+"/"+name, _POST, token=token)
    
    """ Run an asynchronous execution """
    #TODO fix
    def run_job(self, name, input_path =""):
        token = self._get_token(name)
        if input:
            files = {'input': open(input_path, "rb")}
            return utils.make_request(self.cluster, "/job/"+name, _POST, file=files, token=token)
        return utils.make_request(self.cluster, "job/"+name, _POST, token=token)

    #TODO get-file, put-file, list-files

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