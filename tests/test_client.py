import pytest
import json
from unittest.mock import patch, mock_open
from oscar_python.client import Client


@pytest.fixture
def options():
    return {
        'cluster_id': 'test_cluster',
        'endpoint': 'http://test.endpoint',
        'user': 'test_user',
        'password': 'test_password',
        'ssl': True,
        'shortname': 'test_shortname',
        'oidc_token': 'test_oidc_token'
    }


def test_basic_auth_client(options):
    client = Client(options)
    assert client.id == options['cluster_id']
    assert client.endpoint == options['endpoint']
    assert client.user == options['user']
    assert client.password == options['password']
    assert client.ssl == options['ssl']


def test_oidc_agent_client(options):
    del options['user']
    client = Client(options)
    assert client.id == options['cluster_id']
    assert client.endpoint == options['endpoint']
    assert client.shortname == options['shortname']
    assert client.ssl == options['ssl']


def test_oidc_client(options):
    del options['user']
    del options['shortname']
    client = Client(options)
    assert client.id == options['cluster_id']
    assert client.endpoint == options['endpoint']
    assert client.oidc_token == options['oidc_token']
    assert client.ssl == options['ssl']


def test_set_auth_type(options):
    client = Client(options)
    assert client._AUTH_TYPE == "basicauth"

    del options['user']
    client = Client(options)
    assert client._AUTH_TYPE == "oidc-agent"

    del options['shortname']
    options['oidc_token'] = 'test_oidc_token'
    client = Client(options)
    assert client._AUTH_TYPE == "oidc"


def test_get_cluster_info(options):
    client = Client(options)
    with patch('oscar_python._utils.make_request') as mock_request:
        client.get_cluster_info()
        mock_request.assert_called_once_with(client, "/system/info", "get")


def test_get_cluster_config(options):
    client = Client(options)
    with patch('oscar_python._utils.make_request') as mock_request:
        client.get_cluster_config()
        mock_request.assert_called_once_with(client, "/system/config", "get")


def test_list_services(options):
    client = Client(options)
    with patch('oscar_python._utils.make_request') as mock_request:
        client.list_services()
        mock_request.assert_called_once_with(client, "/system/services", "get")


def test_get_service(options):
    client = Client(options)
    with patch('oscar_python._utils.make_request') as mock_request:
        client.get_service("test_service")
        mock_request.assert_called_once_with(client, "/system/services/test_service", "get")


def test_create_service_from_dict(options):
    client = Client(options)
    service_definition = {"name": "test_service"}
    with patch('oscar_python._utils.make_request') as mock_request:
        client.create_service(service_definition)
        mock_request.assert_called_with(client, "/system/services", "post",
                                        data=json.dumps(service_definition))


def test_create_service_from_file(options):
    client = Client(options)
    service_definition = "functions:\n  oscar:\n    - test_cluster:\n        name: test_service\n        script: test_script\n        cpu: 1"
    service_file = "path/to/service.yaml"
    with patch('os.path.isfile', return_value=True), \
         patch('builtins.open', mock_open(read_data=service_definition)), \
         patch('oscar_python._utils.make_request') as mock_request:
        client.create_service(service_file)
        assert mock_request.call_args[0][0] == client
        assert mock_request.call_args[0][1] == "/system/services"
        assert mock_request.call_args[0][2] == "post"
        assert json.loads(mock_request.call_args[1]['data']) == {"name": "test_service",
                                                                 "cpu": "1",
                                                                 "script": service_definition}


def test_update_service_from_dict(options):
    client = Client(options)
    new_service = {"name": "test_service"}
    with patch('oscar_python._utils.make_request') as mock_request:
        mock_request.return_value.status_code = 200
        client.update_service("test_service", new_service)
        mock_request.assert_called_with(client, "/system/services",
                                        "put", data=json.dumps(new_service))


def test_remove_service(options):
    client = Client(options)
    with patch('oscar_python._utils.make_request') as mock_request:
        client.remove_service("test_service")
        mock_request.assert_called_once_with(client, "/system/services/test_service", "delete")
