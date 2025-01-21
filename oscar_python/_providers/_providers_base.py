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

import abc


class StorageProvider(abc.ABC):
    @abc.abstractmethod
    def download_file(self, local_path, remote_path):
        """Generic method to be implemented by all the storage providers."""

    @abc.abstractmethod
    def upload_file(self, local_path, remote_path):
        """Generic method to be implemented by all the storage providers."""

    @abc.abstractmethod
    def list_files_from_path(self, path):
        """Generic method to be implemented by all the storage providers."""

    @abc.abstractmethod
    def _get_client(self):
        """Generic method to be implemented by all the storage providers."""
