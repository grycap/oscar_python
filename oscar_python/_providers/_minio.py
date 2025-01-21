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

import boto3
from oscar_python._providers._s3 import S3

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
