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

from aiohttp import ClientError
import boto3
from oscar_python._providers._providers_base import StorageProvider


class S3(StorageProvider):
    def __init__(self, credentials) -> None:
        super().__init__()
        self.client = self._get_client(credentials)
        self.resource = self._get_resource(credentials)

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

    def _get_resource(self, c):
        if c is None:
            return boto3.resource('s3')
        region = c["region"]
        if region == '':
            region = None
        return boto3.resource('s3',
                              region_name=region,
                              aws_access_key_id=c["access_key"],
                              aws_secret_access_key=c["secret_key"])

    def list_files_from_path(self, path):
        prefix = ""
        path_split = path.split('/')
        bucket = path_split[0]
        if len(path_split) > 1:
            prefix = path.split('/', 2)[1]
        print("Reading content from path:", path)
        return self.client.list_objects(Bucket=bucket, Prefix=prefix)

    def upload_file(self, local_path, remote_path):
        bucket_name = remote_path.split('/')[0]
        file_key = remote_path.split('/', 1)[1]
        file_name = local_path.split('/')[-1]
        print("Uploading to bucket '{0}' with key '{1}'".format(bucket_name,file_key))
        with open(local_path, 'rb') as data:
            try:
                self.client.upload_fileobj(data, bucket_name, file_key + "/" + file_name)
                return True
            except ClientError as err:
                print("Error uploading file: ", err)
                return False

    def download_file(self, local_path, remote_path):
        bucket_name = remote_path.split('/')[0]
        file_key = remote_path.split('/', 1)[1]
        file_path = local_path+"/"+remote_path.split('/')[-1]
        print("Downloading from bucket '{0}' to path '{1}' with key '{2}'".format(bucket_name, file_path, file_key))
        with open(file_path, 'wb') as data:
            try:
                self.client.download_fileobj(bucket_name, file_key, data)
                return True
            except ClientError as err:
                print("Error downloading file: ", err)
                return False
