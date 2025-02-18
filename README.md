## Python OSCAR client

[![Build](https://github.com/grycap/oscar_python/actions/workflows/main.yaml/badge.svg)](https://github.com/grycap/oscar_python/actions/workflows/main.yaml)
![PyPI](https://img.shields.io/pypi/v/oscar_python)

This package provides a client to interact with OSCAR (https://oscar.grycap.net) clusters and services. It is available on Pypi with the name [oscar-python](https://pypi.org/project/oscar-python/).

### Contents
- [Python OSCAR client](#python-oscar-client)
  - [Contents](#contents)
  - [Client](#client)
    - [Initialize a client with basic authentication](#initialize-a-client-with-basic-authentication)
    - [Initialize a client OIDC authentication](#initialize-a-client-oidc-authentication)
  - [Sample usage](#sample-usage)
  - [Client methods](#client-methods)
    - [Cluster methods](#cluster-methods)
    - [Service methods](#service-methods)
    - [Logs methods](#logs-methods)
    - [Storage usage](#storage-usage)

### Client

#### Initialize a client with basic authentication
``` python
  options_basic_auth = {'cluster_id':'cluster-id',
                'endpoint':'https://cluster-endpoint',
                'user':'username',
                'password':'password',
                'ssl':'True'}

  client = Client(options = options_basic_auth)
```
#### Initialize a client OIDC authentication

If you want to use OIDC tokens to authenticate with EGI Check-In, you can use the [OIDC Agent](https://indigo-dc.gitbook.io/oidc-agent/) to create an account configuration for the EGI issuer (https://aai.egi.eu/auth/realms/egi/) and then initialize the client specifying the `shortname` of your account like follows.

``` python
  options_oidc_auth = {'cluster_id':'cluster-id',
                'endpoint':'https://cluster-endpoint',
                'shortname':'oidc-agent-shortname',
                'ssl':'True'}
                
  client = Client(options = options_oidc_auth)
```

If you already have a valid token, you can use the parameter `oidc_token` instead.

``` python
  options_oidc_auth = {'cluster_id':'cluster-id',
                'endpoint':'https://cluster-endpoint',
                'oidc_token':'token',
                'ssl':'True'}
                
  client = Client(options = options_oidc_auth)
```
An example of using a generated token is if you want to use EGI Notebooks. Since you can't use oidc-agent on the Notebook, you can make use of the generated token that EGI provides on path `/var/run/secrets/egi.eu/access_token`.

### Sample usage

- Sample code that creates a client and gets information about the cluster

``` python
from oscar_python.client import Client

options_basic_auth = {'cluster_id':'cluster-id',
              'endpoint':'https://cluster-endpoint',
              'user':'username',
              'password':'password',
              'ssl':'True'}

client = Client(options = options)

# get the cluster information
try:
  info = client.get_cluster_info()
  print(info.text)
except Exception as err:
  print("Failed with: ", err)
```

- Sample code to create a simple service with the [cowsay example](https://github.com/grycap/oscar/tree/master/examples/cowsay) and make a synchronous invocation.

``` python
from oscar_python.client import Client

options_basic_auth = {'cluster_id':'cluster-id',
              'endpoint':'https://cluster-endpoint',
              'user':'username',
              'password':'password',
              'ssl':'True'}

client = Client(options = options)

try:
  client.create_service("/absolute_path/cowsay.yaml")
  response = client.run_service("cowsay", input = '{"message": "Hi there"}')   
  if response.status_code == 200:
      print(response.text)
except Exception as err:
  print("Failed with: ", err)
```

### Client methods

#### Cluster methods

**get_cluster_info**
``` python
# get the cluster information
info = client.get_cluster_info() # returns an HTTP response or an HTTPError
```

**get_cluster_config**
``` python
# get the cluster config
config = client.get_cluster_config() # returns an http response or an HTTPError
```

#### Service methods

**get_service**
``` python
# get the definition of a service 
service = client.get_service("service_name") # returns an http response or an HTTPError
```

**list_services**
``` python
# get a list of all the services deployed 
services = client.list_services() # returns an http response or an HTTPError
```

> _Note_ : Both `path_to_fdl` and the script path inside the fdl must be absolute.

**create_service**
``` python
# create a service 
err = client.create_service("path_to_fdl" | "JSON_definition") # returns nothing if the service is created or an error if something goes wrong
```

**update_service**
``` python
# update a service 
err = client.update_service("service_name","path_to_fdl" | "JSON_definition") # returns nothing if the service is created or an error if something goes wrong
```

**remove_service**
``` python
# remove a service 
response = client.remove_service("service_name") # returns an http response
```

**run_service**

 *`input`, `output` and `timeout` are optional parameters.*

``` python
# make a synchronous execution 
response = client.run_service("service_name", input="input", output="out.png", timeout=100) # returns an http response

# make an asynchronous execution
response = client.run_service("service_name", input="input", async_call=True) # returns an http response
```

#### Logs methods

**get_job_logs**
``` python
# get logs of a job
logs = client.get_job_logs("service_name", "job_id") # returns an http response
```

**list_jobs**
``` python
# get a list of jobs in a service
log_list = client.list_jobs("service_name") # returns an http response
```

**remove_job**
``` python
# remove a job of a service
response = client.remove_job("service_name", "job_id") # returns an http response
```

**remove_all_jobs**
``` python
# remove all jobs in a service
response = client.remove_all_jobs("service_name") # returns an http response
```

#### Storage usage

You can create a storage object to operate over the different storage providers defined on a service with the method `create_storage_client` as follows:

``` python
storage_service = client.create_storage_client("service_name") # returns a storage object
```
> _Note_ : The `storage_provider` parameter on the storage methods follows the format: `["storage_provider_type"].["storage_provider_name"]` where `storage_provider_type` is one of the suported storage providers (minIO, S3, Onedata or webdav) and `storage_provider_name` is the identifier _(ex: minio.default)_

**list_files_from_path**

This method returns a JSON with the info except for OneData, which returns an HTTP response.

``` python
# get a list of the files of one of the service storage provider 
files = storage_service.list_files_from_path("storage_provider") # returns json
```

**upload_file**
``` python
# upload a file from a local path to a remote path 
response = storage_service.upload_file("storage_provider", "local_path", "remote_path")
```

**download_file**
``` python
# download a file from a remote path to a local path 
response = storage_service.download_file("storage_provider", "local_path", "remote_path")
```
