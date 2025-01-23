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

from oscar_python._providers._providers_base import StorageProvider
from webdav3.client import Client
from webdav3.exceptions import WebDavException


class WebDav(StorageProvider):
    def __init__(self, credentials) -> None:
        self.client = self._get_client(credentials)

    def _get_client(self, c):
        """Returns a WebDav client to connect to the https endpoint of the storage provider"""
        hostname = c["hostname"]
        if 'https://' not in hostname:
            hostname = 'https://'+hostname
        options = {
            'webdav_hostname': hostname,
            'webdav_login':    c["login"],
            'webdav_password': c["password"]
        }
        return Client(options=options)

    def upload_file(self, local_path, remote_path):
        file_name = local_path.split('/')[-1]
        if not self.client.check(remote_path):
            try:
                self.client.mkdir(remote_path)
            except WebDavException as exception:
                print("error creating remote path '{0}': {1}".format(remote_path, exception))
                return exception
        try:
            self.client.upload_sync(remote_path+"/"+file_name, local_path)
        except WebDavException as exception:
            print("error uploading file to path '{0}': {1}".format(remote_path+"/"+file_name, exception))

    def download_file(self, local_path, remote_path):
        file_name = remote_path.split('/')[-1]
        try:
            self.client.download_sync(remote_path, local_path+"/"+file_name)
        except WebDavException as exception:
            print("error downloading file from path '{0}': {1}".format(remote_path, exception))

    def list_files_from_path(self, path):
        return self.client.list(path)
