import pytest
from oscar_python._providers._s3 import S3
from unittest.mock import MagicMock, patch, mock_open


@pytest.fixture
def s3_client():
    credentials = {
        "access_key": "access_key",
        "secret_key": "secret_key",
        "region": "region"
    }
    return S3(credentials)


def test_s3_initialization(s3_client):
    assert s3_client is not None


def test_s3_upload_file(s3_client):
    s3_client.client = MagicMock(["upload_fileobj"])
    with patch("builtins.open", mock_open(read_data="data")) as mock_file:
        result = s3_client.upload_file('path/file.txt', 'test_bucket/folder')
        mock_file.assert_called_once_with("path/file.txt", "rb")
        s3_client.client.upload_fileobj.assert_called_once()
        s3_client.client.upload_fileobj.call_args[0][1] == 'test_bucket'
        s3_client.client.upload_fileobj.call_args[0][2] == 'folder/file.txt'
    assert result is True


def test_s3_download_file(s3_client):
    s3_client.client = MagicMock(["download_fileobj"])
    with patch("builtins.open", mock_open()) as mock_file:
        result = s3_client.download_file('path/folder', 'test_bucket/file.txt')
        mock_file.assert_called_once_with("path/folder/file.txt", "wb")
        s3_client.client.download_fileobj.assert_called_once()
        s3_client.client.download_fileobj.call_args[0][1] == 'test_bucket'
        s3_client.client.download_fileobj.call_args[0][2] == 'folder/file.txt'
    assert result is True


def test_s3_list_files(s3_client):
    s3_client.client = MagicMock(["list_objects"])
    s3_client.client.list_objects.return_value = ['file1', 'file2']
    result = s3_client.list_files_from_path('test_bucket/*.txt')
    assert result == ['file1', 'file2']
    s3_client.client.list_objects.assert_called_once_with(Bucket='test_bucket',
                                                          Prefix='*.txt')
