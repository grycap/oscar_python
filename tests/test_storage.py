import pytest
from unittest.mock import MagicMock, patch
from oscar_python.storage import Storage


@pytest.fixture
def mock_client_obj():
    return MagicMock()


@pytest.fixture
def storage(mock_client_obj):
    mock_response = MagicMock()
    mock_response.text = '{"storage_providers": {"minio": {"default": {"access_key": "key","secret_key": "secret", "endpoint": "http://test.endpoint", "region": "us-east-1", "verify": false}}}}'
    with patch('oscar_python._utils.make_request', return_value=mock_response):
        return Storage(mock_client_obj, "test_service")


def test_get_provider_creds(storage):
    creds = storage._get_provider_creds("minio", "default")
    assert creds["access_key"] == "key"
    assert creds["secret_key"] == "secret"


def test_get_client_minio(storage):
    client = storage._get_client("minio.default")
    assert client.__class__.__name__ == "Minio"


def test_list_files_from_path(storage):
    with patch.object(storage, '_get_client') as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        storage.list_files_from_path("minio.default", "/path")
        mock_client.list_files_from_path.assert_called_once_with("/path")


def test_upload_file(storage):
    with patch.object(storage, '_get_client') as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        storage.upload_file("minio.default", "/local/path", "/remote/path")
        mock_client.upload_file.assert_called_once_with("/local/path", "/remote/path")


def test_download_file(storage):
    with patch.object(storage, '_get_client') as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        storage.download_file("minio.default", "/local/path", "/remote/path")
        mock_client.download_file.assert_called_once_with("/local/path", "/remote/path")
