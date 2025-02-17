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

from oscar_python._providers._minio import Minio
from oscar_python._providers._webdav import WebDav
from oscar_python._providers._s3 import S3
from oscar_python._providers._onedata import Onedata
import oscar_python._utils as utils
import json

_MINIO = "minio"
_S3 = "s3"
_ONE_DATA = "onedata"
_WEBDAV = "webdav"
_SVC_PATH = "/system/services"


# TODO check returns from functions
class Storage:
    def __init__(self, client_obj, svc_name) -> None:
        self.client_obj = client_obj
        self.svc_name = svc_name
        self._store_providers()

    """ Function to store all the providers of the service """
    def _store_providers(self):
        svc = utils.make_request(self.client_obj, _SVC_PATH + "/" + self.svc_name, "get")
        self.storage_providers = json.loads(svc.text)["storage_providers"]

    """ Function to retreive credentials of a specific storage provider """
    def _get_provider_creds(self, provider, provider_name):
        return self.storage_providers[provider][provider_name]

    def _get_client(self, storage_provider):
        provider = storage_provider.split('.')[0]
        provider_name = storage_provider.split('.')[1]
        creds = self._get_provider_creds(provider, provider_name)

        if provider == _MINIO:
            return Minio(credentials=creds)
        elif provider == _WEBDAV:
            return WebDav(credentials=creds)
        elif provider == _S3:
            return S3(credentials=creds)
        elif provider == _ONE_DATA:
            return Onedata(credentials=creds)
        else:
            print('Error: storage provider "{0}" is not defined in service "{1}"'.format(storage_provider, self.svc_name))
            return False

    """ The 'storage_provider' parameter follows the format:
        [storage_provider_type].[storage_provider_name]
        where 'storage_provider_type' is one of the suported storage providers
        (minIO, S3, Onedata or webdav) and 'storage_provider_name' is the identifier
        (ex: minio.default) """

    """ List content of the service folders. """
    def list_files_from_path(self, storage_provider, path):
        client = self._get_client(storage_provider)
        return client.list_files_from_path(path)

    """ Upload file from a local path to a remote path. """
    def upload_file(self, storage_provider, local_path, remote_path):
        client = self._get_client(storage_provider)
        client.upload_file(local_path, remote_path)

    """ Download file from a remote path to a local path. """
    def download_file(self, storage_provider, local_path, remote_path):
        client = self._get_client(storage_provider)
        client.download_file(local_path, remote_path)
