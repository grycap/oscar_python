from _providers._providers_base import StorageProvider
import requests

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

    #TODO 
    def upload_file(self, local_path, remote_path):
        file_name = local_path.split('/')[-1]

    #TODO  
    def download_file(self, local_path, remote_path):
        return super().download_file(local_path, remote_path)

    def _folder_exists(self, folder_name):
        url = (f'https://{self.oneprovider_host}{self._CDMI_PATH}/'
               f'{self.oneprovider_space}/{folder_name}/')
        headers = {**self._CDMI_VERSION_HEADER, **self.headers}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return True
        return False
    
    def _create_folder(self, folder_name):
        url = (f'https://{self.oneprovider_host}{self._CDMI_PATH}/'
               f'{self.oneprovider_space}/{folder_name}/')
        response = requests.put(url, headers=self.headers)
        if response.status_code != 201: 
            return False