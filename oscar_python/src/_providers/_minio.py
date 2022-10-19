import boto3
from _providers._s3 import S3

_DEFAULT_MINIO_ENDPOINT = 'http://minio-service.minio:9000'

class Minio(S3):
   
    def _get_client(self, c):
        """Return Minio client with user configuration."""
        if c["endpoint"] == '':
            c["endpoint"] = _DEFAULT_MINIO_ENDPOINT
        if c["region"] == '':
            c["region"] = None
        return boto3.client('s3',
                            endpoint_url=c["endpoint"],
                            region_name=c["region"],
                            verify=c["verify"],
                            aws_access_key_id=c["access_key"],
                            aws_secret_access_key=c["secret_key"])