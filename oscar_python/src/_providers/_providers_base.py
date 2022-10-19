import abc

class StorageProvider(abc.ABC):
    @abc.abstractmethod
    def download_file(self, local_path, remote_path):
        """Generic method to be implemented by all the storage providers."""

    @abc.abstractmethod
    def upload_file(self, local_path, remote_path):
        """Generic method to be implemented by all the storage providers."""
    
    @abc.abstractmethod
    def _get_client(self):
        """Generic method to be implemented by all the storage providers."""