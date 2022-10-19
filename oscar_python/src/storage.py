from _providers._minio import Minio
from _providers._webdav import WebDav
from _providers._s3 import S3
from _providers._onedata import Onedata
import _utils as utils
import json

_MINIO = "minio"
_S3 = "s3"
_ONE_DATA = "onedata"
_WEBDAV = "webdav"
_SVC_PATH = "/system/services"

class Storage:
    def __init__(self, service, svc_name) -> None:
        self.service = service
        self.svc_name = svc_name
        self._store_providers()

    """ Function to store all the providers of the service """
    def _store_providers(self):
        svc = utils.make_request(self.service.cluster, _SVC_PATH+"/"+self.svc_name, "get")
        self.storage_providers = json.loads(svc.text)["storage_providers"]
    
    """ Function to retreive credentials of a specific storage provider """
    def _get_provider_creds(self, provider,provider_name):
        return self.storage_providers[provider][provider_name]

    """ Upload file from a local path to a remote path. 
        The 'storage_provider' parameter follows the format:
        [storage_provider_type].[storage_provider_name]
        where 'storage_provider_type' is one of the suported storage providers
        (minIO, S3, Onedata or webdav) and 'storage_provider_name' is the identifier
        (ex: minio.default) """
    def upload_file(self, storage_provider, local_path, remote_path):
        self._do(storage_provider, local_path, remote_path, "upload")

    """ Download file from a remote path to a local path
        The 'storage_provider' parameter follows the format:
        [storage_provider_type].[storage_provider_name]
        where 'storage_provider_type' is one of the suported storage providers
        (minIO, S3, Onedata or webdav) and 'storage_provider_name' is the identifier
        (ex: minio.default) """
    def download_file(self, storage_provider, local_path, remote_path):
        self._do(storage_provider, local_path, remote_path, "download")
    
    def _do(self, storage_provider, local_path, remote_path, operation):
        provider = storage_provider.split('.')[0]
        provider_name = storage_provider.split('.')[1]
        creds = self._get_provider_creds(provider, provider_name)

        if provider == _MINIO:      
           client = Minio(credentials=creds)
        elif provider == _WEBDAV: 
           client = WebDav(credentials=creds)
        elif provider == _S3:
            client = S3(credentials=creds)
        elif provider == _ONE_DATA:
            client = Onedata(credentials=creds)
        else:
            print('error: storage provider "{0}" is not defined in service "{1}"'.format(storage_provider, self.svc_name))
            return False
        
        if operation == "upload": client.upload_file(local_path,remote_path)
        if operation == "download": client.download_file(local_path,remote_path)