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

    del options['oidc_token']
    options['refresh_token'] = 'test_refresh_token'
    options['scopes'] = ['openid', 'profile', 'email']
    options['token_endpoint'] = 'test_token_endpoint'
    client = Client(options)
    assert client.refresh_token == options['refresh_token']
    assert client.scopes == ['openid', 'profile', 'email']
    assert client.token_endpoint == options['token_endpoint']


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
    service_definition = (
        "functions:\n  oscar:\n    - test_cluster:\n"
        "        name: test_service\n"
        "        script: test_script\n"
        "        cpu: 1"
    )
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


def test_health_check(options):
    client = Client(options)
    with patch('oscar_python._utils.make_request') as mock_request:
        client.health_check()
        mock_request.assert_called_once_with(client, "/health", "get")


def test_get_deployment_status(options):
    client = Client(options)
    with patch('oscar_python._utils.make_request') as mock_request:
        client.get_deployment_status("test_service")
        mock_request.assert_called_once_with(client, "/system/services/test_service/deployment", "get")


def test_get_deployment_logs(options):
    client = Client(options)
    with patch('oscar_python._utils.make_request') as mock_request:
        client.get_deployment_logs("test_service")
        mock_request.assert_called_once_with(client, "/system/services/test_service/deployment/logs", "get")


def test_list_volumes(options):
    client = Client(options)
    with patch('oscar_python._utils.make_request') as mock_request:
        client.list_volumes()
        mock_request.assert_called_once_with(client, "/system/volumes", "get")


def test_create_volume(options):
    client = Client(options)
    with patch('oscar_python._utils.make_request') as mock_request:
        client.create_volume("test_vol", "1Gi")
        mock_request.assert_called_once_with(client, "/system/volumes", "post",
                                             data=json.dumps({"name": "test_vol", "size": "1Gi"}))


def test_get_volume(options):
    client = Client(options)
    with patch('oscar_python._utils.make_request') as mock_request:
        client.get_volume("test_vol")
        mock_request.assert_called_once_with(client, "/system/volumes/test_vol", "get")


def test_delete_volume(options):
    client = Client(options)
    with patch('oscar_python._utils.make_request') as mock_request:
        client.delete_volume("test_vol")
        mock_request.assert_called_once_with(client, "/system/volumes/test_vol", "delete")


def test_list_buckets(options):
    client = Client(options)
    with patch('oscar_python._utils.make_request') as mock_request:
        client.list_buckets()
        mock_request.assert_called_once_with(client, "/system/buckets", "get")


def test_get_bucket(options):
    client = Client(options)
    with patch('oscar_python._utils.make_request') as mock_request:
        client.get_bucket("test_bucket")
        mock_request.assert_called_once_with(client, "/system/buckets/test_bucket", "get")


def test_create_bucket(options):
    client = Client(options)
    with patch('oscar_python._utils.make_request') as mock_request:
        client.create_bucket("test_bucket")
        mock_request.assert_called_once_with(
            client, "/system/buckets", "post",
            data=json.dumps({"bucket_name": "test_bucket",
                             "visibility": "private",
                             "allowed_users": []}))


def test_create_bucket_with_visibility(options):
    client = Client(options)
    with patch('oscar_python._utils.make_request') as mock_request:
        client.create_bucket("test_bucket", visibility="public", allowed_users=["user1"])
        mock_request.assert_called_once_with(
            client, "/system/buckets", "post",
            data=json.dumps({"bucket_name": "test_bucket",
                             "visibility": "public",
                             "allowed_users": ["user1"]}))


def test_update_bucket(options):
    client = Client(options)
    with patch('oscar_python._utils.make_request') as mock_request:
        client.update_bucket("test_bucket", "public", ["user1"])
        mock_request.assert_called_once_with(
            client, "/system/buckets", "put",
            data=json.dumps({"bucket_name": "test_bucket",
                             "visibility": "public",
                             "allowed_users": ["user1"]}))


def test_delete_bucket(options):
    client = Client(options)
    with patch('oscar_python._utils.make_request') as mock_request:
        client.delete_bucket("test_bucket")
        mock_request.assert_called_once_with(client, "/system/buckets/test_bucket", "delete")


def test_presign_bucket(options):
    client = Client(options)
    with patch('oscar_python._utils.make_request') as mock_request:
        client.presign_bucket("test_bucket", "file.txt", operation="upload", expires=3600)
        mock_request.assert_called_once_with(
            client, "/system/buckets/test_bucket/presign", "post",
            data=json.dumps({"object_key": "file.txt",
                             "operation": "upload",
                             "expires": 3600,
                             "content_type": "",
                             "extra_headers": {}}))


def test_get_system_logs(options):
    client = Client(options)
    with patch('oscar_python._utils.make_request') as mock_request:
        client.get_system_logs()
        mock_request.assert_called_once_with(client, "/system/logs", "get")


def test_get_system_logs_with_flags(options):
    client = Client(options)
    with patch('oscar_python._utils.make_request') as mock_request:
        client.get_system_logs(timestamps=True, previous=True)
        mock_request.assert_called_once_with(client, "/system/logs?timestamps=true&previous=true", "get")


def test_get_metrics_summary(options):
    client = Client(options)
    with patch('oscar_python._utils.make_request') as mock_request:
        client.get_metrics_summary()
        mock_request.assert_called_once_with(client, "/system/metrics", "get")


def test_get_metrics_breakdown(options):
    client = Client(options)
    with patch('oscar_python._utils.make_request') as mock_request:
        client.get_metrics_breakdown("user")
        mock_request.assert_called_once_with(client, "/system/metrics/breakdown?group_by=user", "get")


def test_get_metrics_breakdown_default(options):
    client = Client(options)
    with patch('oscar_python._utils.make_request') as mock_request:
        client.get_metrics_breakdown()
        mock_request.assert_called_once_with(client, "/system/metrics/breakdown?group_by=service", "get")


def test_get_service_metrics(options):
    client = Client(options)
    with patch('oscar_python._utils.make_request') as mock_request:
        client.get_service_metrics("test_service")
        mock_request.assert_called_once_with(client, "/system/metrics/test_service", "get")


def test_get_own_quota(options):
    client = Client(options)
    with patch('oscar_python._utils.make_request') as mock_request:
        client.get_own_quota()
        mock_request.assert_called_once_with(client, "/system/quotas/user", "get")


def test_get_user_quota(options):
    client = Client(options)
    with patch('oscar_python._utils.make_request') as mock_request:
        client.get_user_quota("test_user")
        mock_request.assert_called_once_with(client, "/system/quotas/user/test_user", "get")


def test_update_user_quota(options):
    client = Client(options)
    with patch('oscar_python._utils.make_request') as mock_request:
        client.update_user_quota("test_user", "2", "4Gi")
        mock_request.assert_called_once_with(client, "/system/quotas/user/test_user", "put",
                                             data=json.dumps({"cpu": "2", "memory": "4Gi"}))


def test_get_federation(options):
    client = Client(options)
    with patch('oscar_python._utils.make_request') as mock_request:
        client.get_federation("test_service")
        mock_request.assert_called_once_with(client, "/system/federation/test_service", "get")


def test_add_federation_members(options):
    client = Client(options)
    members = [{"type": "oscar", "cluster_id": "c1", "service_name": "s1", "priority": 0}]
    with patch('oscar_python._utils.make_request') as mock_request:
        client.add_federation_members("test_service", members)
        mock_request.assert_called_once_with(
            client, "/system/federation/test_service", "post",
            data=json.dumps({"members": members}))


def test_add_federation_members_with_clusters(options):
    client = Client(options)
    members = [{"type": "oscar", "cluster_id": "c1", "service_name": "s1", "priority": 0}]
    clusters = {"c1": {"endpoint": "https://c1.com", "auth_user": "u", "auth_password": "p"}}
    with patch('oscar_python._utils.make_request') as mock_request:
        client.add_federation_members("test_service", members, clusters=clusters)
        mock_request.assert_called_once_with(
            client, "/system/federation/test_service", "post",
            data=json.dumps({"members": members, "clusters": clusters}))


def test_add_federation_members_with_storage_providers(options):
    client = Client(options)
    members = [{"type": "oscar", "cluster_id": "c1", "service_name": "s1", "priority": 0}]
    clusters = {"c1": {"endpoint": "https://c1.com", "auth_user": "u", "auth_password": "p"}}
    storage_providers = {"minio": {"my-minio": {"endpoint": "https://minio.com", "access_key": "ak", "secret_key": "sk"}}}
    with patch('oscar_python._utils.make_request') as mock_request:
        client.add_federation_members("test_service", members, clusters=clusters,
                                      storage_providers=storage_providers)
        mock_request.assert_called_once_with(
            client, "/system/federation/test_service", "post",
            data=json.dumps({"members": members, "clusters": clusters,
                             "storage_providers": storage_providers}))


def test_update_federation_members(options):
    client = Client(options)
    members = [{"type": "oscar", "cluster_id": "c1", "service_name": "s1", "priority": 0}]
    update = [{"type": "oscar", "cluster_id": "c1", "service_name": "s1", "priority": 5}]
    with patch('oscar_python._utils.make_request') as mock_request:
        client.update_federation_members("test_service", members, update)
        mock_request.assert_called_once_with(
            client, "/system/federation/test_service", "put",
            data=json.dumps({"members": members, "update": update}))


def test_update_federation_members_with_clusters(options):
    client = Client(options)
    members = [{"type": "oscar", "cluster_id": "c1", "service_name": "s1", "priority": 0}]
    update = [{"type": "oscar", "cluster_id": "c1", "service_name": "s1", "priority": 5}]
    clusters = {"c1": {"endpoint": "https://c1.com", "auth_user": "u", "auth_password": "new"}}
    storage_providers = {"minio": {"my-minio": {"endpoint": "https://minio.com", "access_key": "ak", "secret_key": "sk"}}}
    with patch('oscar_python._utils.make_request') as mock_request:
        client.update_federation_members("test_service", members, update,
                                         clusters=clusters, storage_providers=storage_providers)
        mock_request.assert_called_once_with(
            client, "/system/federation/test_service", "put",
            data=json.dumps({"members": members, "update": update,
                             "clusters": clusters, "storage_providers": storage_providers}))


def test_remove_federation_members(options):
    client = Client(options)
    members = [{"type": "oscar", "cluster_id": "c1", "service_name": "s1", "priority": 0}]
    with patch('oscar_python._utils.make_request') as mock_request:
        client.remove_federation_members("test_service", members)
        mock_request.assert_called_once_with(
            client, "/system/federation/test_service", "delete",
            data=json.dumps({"members": members, "delete": False}))


def test_remove_federation_members_with_delete(options):
    client = Client(options)
    members = [{"type": "oscar", "cluster_id": "c1", "service_name": "s1", "priority": 0}]
    with patch('oscar_python._utils.make_request') as mock_request:
        client.remove_federation_members("test_service", members, delete=True)
        mock_request.assert_called_once_with(
            client, "/system/federation/test_service", "delete",
            data=json.dumps({"members": members, "delete": True}))
