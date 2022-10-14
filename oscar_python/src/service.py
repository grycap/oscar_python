from cluster import Cluster
import _utils as utils
import json
import yaml

_SVC_PATH = "/system/services"
_RUN_PATH = "/run"
_GET = "get"
_POST = "post"
_PUT = "put"
_DELETE = "delete"

class Service:
    def __init__(self, cluster: Cluster) -> None:
        self.cluster = cluster

    """ List all services from the """
    def listServices(self):
        return utils.makeRequest(self.cluster, _SVC_PATH, _GET)
    
    def getService(self, name):
        return utils.makeRequest(self.cluster, _SVC_PATH+"/"+name, _GET)

    """ Create a service on a specific cluster from a FDL file """
    def createService(self, fdlPath):
        with open(fdlPath, "r") as read_fdl:
            fdl = self._parseFDLyaml(read_fdl)
        if fdl != ValueError:
            for element in fdl["functions"]["oscar"]:
                try:
                    svc = element[self.cluster.id]
                except KeyError as err:
                    print("Error: FDL clusterID don't match current clusterID: {0}".format(err))
                    return False
                try:
                    with open(svc["script"]) as s:
                        svc["script"] = s.read()
                except IOError as err:
                    print("Error: Couldn't read script")
                    print("Service script path: ",svc["script"])

                # cpu parameter has to be string on the request
                if type(svc["cpu"]) is int or type(svc["cpu"]) is float: svc["cpu"]= str(svc["cpu"])
                print(json.dumps(svc))
                return utils.makeRequest(self.cluster, _SVC_PATH, _POST, json.dumps(svc))
        else:
            print("Error: Bad yaml format: {0}".format(fdl))
            return False

    def removeService(self, name):
        return utils.makeRequest(self.cluster, _SVC_PATH+"/"+name, _DELETE)

    def runService(self, name, input=None):
        pass

    #TODO get-file, put-file, list-files

    def _parseFDLyaml(self, fdlPointer):
        try:
            fdl_yaml = yaml.safe_load(fdlPointer)
        except ValueError as err:
            return err
        return fdl_yaml 

class Logs:
    def __init__(self, cluster: Cluster) -> None:
        self.cluster = cluster 
    
    def getJobLogs(self, svc):
        pass

    def listJobsLogs(self, svc):
        pass

    def removeJobsLogs(self):
        pass