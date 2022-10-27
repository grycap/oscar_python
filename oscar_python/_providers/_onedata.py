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
import requests
import json

#TODO fix error returns
class Onedata(StorageProvider):
    
    _CDMI_PATH = '/cdmi'
    _CDMI_VERSION_HEADER = {'X-CDMI-Specification-Version': '1.1.1'}

    def __init__(self, credentials) -> None:
        super().__init__()
        self._get_client(credentials)
    
    def _get_client(self, c):
        self.oneprovider_space = c["space"]
        self.oneprovider_host = c["oneprovider_host"]
        self.headers = {'X-Auth-Token': c["token"]}
        self.url = (f'https://{self.oneprovider_host}{self._CDMI_PATH}/'
                    f'{self.oneprovider_space}/')
    
    def upload_file(self, local_path, remote_path):
        file_name = local_path.split('/')[-1]
        if not self._folder_exists(remote_path):
            folders = remote_path.split('/')
            path = ''
            for folder in folders:
                path = f'{path}/{folder}'
                if not self._folder_exists(path):
                    print("folder '{0}' doesn't exist. Creating folder...", folder)
                    if not self._create_folder(path):
                        print("couldn't create folder: ", path)
                        return
        url = self.url+remote_path+"/"+file_name
        print("Uploading file to endpoint: ", url)
        with open(local_path, 'rb') as data:
            response = requests.put(url, data=data, headers=self.headers)
            if response.status_code not in [201, 202, 204]:
                print("PostError: error uploading file {0} to url: {1}".format(file_name, url))
                return response

    def download_file(self, local_path, remote_path):
        file_name = remote_path.split('/')[-1]
        url = self.url+remote_path
        res = requests.get(url=url, headers=self.headers)
        if res.status_code == 200: print("Saving file to {0}/{1}".format(local_path, file_name))
        self._save_file(local_path+"/"+file_name, res.content, mode='wb')
    
    def list_files_from_path(self, path):
        headers = {**self._CDMI_VERSION_HEADER, **self.headers}
        return requests.get(url = self.url+path+"/", headers=headers)

    def _save_file(self, path, content, mode='w'):
        with open(path, mode) as fwc:
            if isinstance(content, dict):
                content = json.dumps(content)
            fwc.write(content)

    def _folder_exists(self, folder_name):
        headers = {**self._CDMI_VERSION_HEADER, **self.headers}
        response = requests.get(url = self.url+folder_name+"/", headers=headers)
        if response.status_code == 200:
            return True
        return False
    
    def _create_folder(self, folder_name):
        response = requests.put(url = self.url+folder_name+"/", headers=self.headers)
        if response.status_code != 201: 
            return False