import pytest
from oscar_python._providers._webdav import WebDav
from unittest.mock import patch, mock_open, MagicMock


@pytest.fixture
def webdav():
    credentials = {
        "hostname": "hostname",
        "login": "login",
        "password": "password"
    }
    return WebDav(credentials)


def test_webdav_initialization(webdav):
    assert isinstance(webdav, WebDav)


def test_webdav_upload_file(webdav):
    webdav.client = MagicMock(["check", "mkdir", "upload_sync"])
    webdav.client.check.return_value = False

    with patch("builtins.open", mock_open()):
        response = webdav.upload_file('local_path/file.txt', 'remote_path')
        assert response is None

    webdav.client.check.assert_called_with('remote_path')
    webdav.client.mkdir.assert_called_with('remote_path')
    webdav.client.upload_sync.assert_called_with('remote_path/file.txt', 'local_path/file.txt')


def test_webdav_download_file(webdav):
    webdav.client = MagicMock(["download_sync"])
    webdav.client.download_sync.return_value = None

    with patch("builtins.open", mock_open()) as mock_file:
        webdav.download_file('local_path', 'remote_path/file.txt')

    webdav.client.download_sync.assert_called_with('remote_path/file.txt', 'local_path/file.txt')


def test_webdav_list_files_from_path(webdav):
    webdav.client = MagicMock(["list"])
    webdav.client.list.return_value = ['file1.txt', 'file2.txt']

    response = webdav.list_files_from_path('path')
    assert response == ['file1.txt', 'file2.txt']

    webdav.client.list.assert_called_with('path')
