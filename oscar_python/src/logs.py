from cluster import Cluster
import _utils as utils

_LOGS_PATH = "/system/logs"
_GET = "get"
_DELETE = "delete"

#TODO test
class Logs:
    def __init__(self, cluster: Cluster) -> None:
        self.cluster = cluster 
    
    def get_job_logs(self, svc, job):
        return utils.make_request(self, _LOGS_PATH+"/"+svc+"/"+job, _GET)

    def list_jobs(self, svc):
        return utils.make_request(self, _LOGS_PATH+"/"+svc, _GET)

    def remove_job(self, svc, job):
        return utils.make_request(self, _LOGS_PATH+"/"+svc+"/"+job, _DELETE)

    def remove_all_jobs(self, svc):
        return utils.make_request(self, _LOGS_PATH+"/"+svc, _DELETE)