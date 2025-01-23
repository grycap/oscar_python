import pytest
from oscar_python._providers._onedata import Onedata
from unittest.mock import MagicMock, patch, mock_open


@pytest.fixture
def onedata():
    credentials = {
        "token": "token",
        "space": "space",
        "oneprovider_host": "oneprovider_host"
    }
    return Onedata(credentials)


def test_onedata_initialization(onedata):
    assert isinstance(onedata, Onedata)


@patch('oscar_python._providers._onedata.requests')
def test_onedata_upload_file(mock_requests, onedata):
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_requests.put.return_value = mock_response
    with patch("builtins.open", mock_open()):
        response = onedata.upload_file('file_path', 'remote_path')
        assert response is None
    mock_requests.get.assert_called_with(
        url='https://oneprovider_host/cdmi/space//remote_path/',
        headers={'X-CDMI-Specification-Version': '1.1.1', 'X-Auth-Token': 'token'}
    )
    mock_requests.put.call_args_list[0][1]['url'] == 'https://oneprovider_host/cdmi/space//remote_path/file_path'
    mock_requests.put.call_args_list[0][1]['headers'] == {'X-Auth-Token', 'token'}

    mock_requests.put.call_args_list[1][0] == 'https://oneprovider_host/cdmi/space//remote_path/file_path'
    mock_requests.put.call_args_list[1][1]['headers'] == {'X-Auth-Token', 'token'}


@patch('oscar_python._providers._onedata.requests')
def test_onedata_download_file(mock_requests, onedata):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'content'
    mock_requests.get.return_value = mock_response
    with patch("builtins.open", mock_open()) as mock_file:
        onedata.download_file('local_path', 'remote_path')
        mock_file.assert_called_with('local_path/remote_path', 'wb')
        mock_file().write.assert_called_with(b'content')
    mock_requests.get.assert_called_with(
        url='https://oneprovider_host/cdmi/space/remote_path',
        headers={'X-Auth-Token': 'token'}
    )
    mock_requests.get.return_value.content == b'content'


@patch('oscar_python._providers._onedata.requests')
def test_onedata_list_files_from_path(mock_requests, onedata):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_requests.get.return_value = mock_response
    response = onedata.list_files_from_path('path')
    assert response == mock_response
    mock_requests.get.assert_called_with(
        url='https://oneprovider_host/cdmi/space/path/',
        headers={'X-CDMI-Specification-Version': '1.1.1', 'X-Auth-Token': 'token'}
    )
