import pytest
from unittest.mock import patch, MagicMock
from oscar_python.default_client import DefaultClient, _RUN_PATH, _POST, _JOB_PATH


class TestDefaultClient(DefaultClient):
    def _get_token(self, name):
        return "test_token"


@pytest.fixture
def client():
    return TestDefaultClient()


@patch('oscar_python._utils.make_request')
@patch('oscar_python._utils.encode_input')
@patch('oscar_python._utils.decode_output')
def test_run_service_with_input_and_token(mock_decode_output, mock_encode_input, mock_make_request, client):
    mock_response = MagicMock()
    mock_response.text = "response_text"
    mock_make_request.return_value = mock_response
    mock_encode_input.return_value = "encoded_input"

    response = client.run_service("test_service", input="test_input", token="test_token", output="output_file", timeout=30)

    mock_encode_input.assert_called_once_with("test_input")
    mock_make_request.assert_called_once_with(client, _RUN_PATH+"/test_service", _POST, data="encoded_input", token="test_token", timeout=30)
    mock_decode_output.assert_called_once_with("response_text", "output_file")
    assert response == mock_response


@patch('oscar_python._utils.make_request')
@patch('oscar_python._utils.encode_input')
def test_run_service_with_input_no_token(mock_encode_input, mock_make_request, client):
    mock_response = MagicMock()
    mock_response.text = "response_text"
    mock_make_request.return_value = mock_response
    mock_encode_input.return_value = "encoded_input"

    response = client.run_service("test_service", input="test_input")

    mock_encode_input.assert_called_once_with("test_input")
    mock_make_request.assert_called_once_with(client, _RUN_PATH+"/test_service", _POST, data="encoded_input", token="test_token", timeout=None)
    assert response == mock_response


@patch('oscar_python._utils.make_request')
def test_run_service_no_input(mock_make_request, client):
    mock_response = MagicMock()
    mock_response.text = "response_text"
    mock_make_request.return_value = mock_response

    response = client.run_service("test_service", input="data")
    mock_make_request.assert_called_with(client, _RUN_PATH+"/test_service", _POST,
                                         token="test_token", data=b'ZGF0YQ==', timeout=None)

    response = client.run_service("test_service", input="data", async_call=True, timeout=30)
    mock_make_request.assert_called_with(client, _JOB_PATH+"/test_service", _POST,
                                         token="test_token", data=b'ZGF0YQ==', timeout=30)
    assert response == mock_response
