import base64
import json
import pytest
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

        def get_access_token(self):
            return "test_oidc_token"

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
        mock_request.assert_called_once_with(
            "post", "http://test.com/test",
            headers={"Authorization": "Bearer test_token", "Content-Type": "application/json"},
            verify=True, data="test_data", timeout=60)


def test_load_config(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({
        "clusters": {
            "default": {
                "endpoint": "http://test.cluster",
                "user": "test_user",
                "password": "test_pass",
                "ssl": False
            }
        }
    }))
    opts = utils.load_config(str(config_file))
    assert opts["cluster_id"] == "default"
    assert opts["endpoint"] == "http://test.cluster"
    assert opts["user"] == "test_user"
    assert opts["password"] == "test_pass"
    assert opts["ssl"] is False


def test_load_config_with_oidc(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({
        "clusters": {
            "oidc_cluster": {
                "endpoint": "http://oidc.cluster",
                "oidc_token": "test_token",
                "ssl": True
            }
        }
    }))
    opts = utils.load_config(str(config_file), "oidc_cluster")
    assert opts["cluster_id"] == "oidc_cluster"
    assert opts["endpoint"] == "http://oidc.cluster"
    assert "user" not in opts
    assert opts["oidc_token"] == "test_token"
    assert opts["ssl"] is True


def test_load_config_missing_cluster(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({"clusters": {}}))
    with pytest.raises(KeyError):
        utils.load_config(str(config_file), "nonexistent")


def test_load_config_minimal(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({
        "clusters": {
            "minimal": {
                "endpoint": "http://minimal.cluster"
            }
        }
    }))
    opts = utils.load_config(str(config_file), "minimal")
    assert opts["endpoint"] == "http://minimal.cluster"
    assert opts["ssl"] is True
    for key in ("user", "password", "shortname", "oidc_token", "refresh_token"):
        assert key not in opts


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
