import boto3
from _providers._providers_base import StorageProvider

class S3(StorageProvider):
    def __init__(self, credentials) -> None:
        super().__init__()
        self.client = self._get_client(credentials)
    
    def _get_client(self, c):
        """Returns S3 client with default configuration."""
        if c is None:
            return boto3.client('s3')
        region = c["region"]
        if region == '':
            region = None
        return boto3.client('s3',
                            region_name=region,
                            aws_access_key_id=c["access_key"],
                            aws_secret_access_key=c["secret_key"])

    def upload_file(self, local_path, remote_path):
        bucket_name = remote_path.split('/')[0]
        file_key = remote_path.split('/',2)[1]
        file_name = local_path.split('/')[-1]
        print("Uploading to bucket {0} with key {1}".format(bucket_name,file_key))
        with open(local_path, 'rb') as data:
            self.client.upload_fileobj(data, bucket_name, file_key+file_name)
  
    def download_file(self, local_path, remote_path):
        bucket_name = remote_path.split('/')[0]
        file_key = remote_path.split('/',2)[1]
        file_path = local_path+"/"+remote_path.split('/')[-1]
        with open(file_path, 'wb') as data:
            self.client.download_fileobj(bucket_name, file_key, data)