from _providers._providers_base import StorageProvider
from webdav3.client import Client

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
            self.client.mkdir(remote_path)
        self.client.upload_sync(remote_path+"/"+file_name, local_path)
    
    def download_file(self, local_path, remote_path):
        file_name = remote_path.split('/')[-1]
        self.client.download_sync(remote_path, local_path+"/"+file_name)