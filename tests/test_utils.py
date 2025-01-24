import base64
from unittest.mock import patch, MagicMock, mock_open

import oscar_python._utils as utils


def test_get_headers_with_basicauth():
    class MockClient:
        _AUTH_TYPE = "basicauth"
        user = "test_user"
        password = "test_password"

    c = MockClient()
    headers = utils.get_headers(c)
    assert headers["Authorization"].startswith("Basic ")


def test_get_headers_with_oidc_agent():
    class MockClient:
        _AUTH_TYPE = "oidc-agent"
        shortname = "test_shortname"

    with patch("liboidcagent.get_access_token", return_value="test_token"):
        c = MockClient()
        headers = utils.get_headers(c)
        assert headers["Authorization"] == "Bearer test_token"


def test_get_headers_with_oidc():
    class MockClient:
        _AUTH_TYPE = "oidc"
        oidc_token = "test_oidc_token"

    c = MockClient()
    headers = utils.get_headers(c)
    assert headers["Authorization"] == "Bearer test_oidc_token"


def test_encode_input_with_string():
    test_data = "test_data"
    encoded = utils.encode_input(test_data)
    assert base64.b64encode(test_data.encode()) == encoded


def test_decode_output_with_base64():
    test_data = base64.b64encode(b"test_data").decode("utf-8")
    with patch("builtins.open", mock_open()) as mock_file:
        utils.decode_output(test_data, "test_output.txt")
        mock_file.assert_called_once_with("test_output.txt", "w")
        mock_file().write.assert_called_once_with("test_data")


def test_decode_output_with_string():
    test_data = base64.b64encode(b"test_data")
    with patch("builtins.open", mock_open()) as mock_file:
        utils.decode_output(test_data, "test_output.txt")
        mock_file.assert_called_once_with("test_output.txt", "w")
        mock_file().write.assert_called_once_with("test_data")


def test_make_request_post():
    class MockClient:
        endpoint = "http://test.com"
        ssl = True
        _AUTH_TYPE = "basicauth"
        user = "test_user"
        password = "test_password"

    c = MockClient()
    with patch("requests.request") as mock_request:
        mock_request.return_value.status_code = 200
        mock_request.return_value.raise_for_status = MagicMock()
        response = utils.make_request(c, "/test", "post", data="test_data", token="test_token")
        assert response.status_code == 200
        mock_request.assert_called_once_with("post", "http://test.com/test", headers={"Authorization": "Bearer test_token"}, verify=True, data="test_data", timeout=60)


def test_make_request_get():
    class MockClient:
        endpoint = "http://test.com"
        ssl = True
        _AUTH_TYPE = "basicauth"
        user = "test_user"
        password = "test_password"

    c = MockClient()
    with patch("requests.request") as mock_request:
        mock_request.return_value.status_code = 200
        mock_request.return_value.raise_for_status = MagicMock()
        response = utils.make_request(c, "/test", "get")
        assert response.status_code == 200
        mock_request.assert_called_once_with("get", "http://test.com/test",
                                             headers={'Authorization': 'Basic dGVzdF91c2VyOnRlc3RfcGFzc3dvcmQ='},
                                             verify=True, timeout=60)
