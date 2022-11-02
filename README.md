## Python OSCAR API

[![Build](https://github.com/grycap/oscar_python/actions/workflows/main.yaml/badge.svg)](https://github.com/grycap/oscar_python/actions/workflows/main.yaml)
![PyPI](https://img.shields.io/pypi/v/oscar_python)

### Contents
- [Python OSCAR API](#python-oscar-api)
  - [Contents](#contents)
  - [Sample usage](#sample-usage)
  - [API methods](#api-methods)
    - [Cluster methods](#cluster-methods)
    - [Service methods](#service-methods)
    - [Logs methods](#logs-methods)
    - [Storage usage](#storage-usage)

### Sample usage

- Sample code that creates a client and gets information about the cluster

``` python
from oscar_python.client import Client

client = Client("cluster-id","https://cluster-endpoint", "username", "password", True)

# get the cluster information
info = client.get_cluster_info()
print(info.text)
```

- Sample code to create a simple service with the [cowsay example](https://github.com/grycap/oscar/tree/master/examples/cowsay) and afterwards make a synchronous invocation.

``` python
from oscar_python.client import Client

client = Client("cluster-id","https://cluster-endpoint", "username", "password", True)

err = client.create_service("/absolute_path/cowsay.yaml")
if not err:
    res = client.run_service("cowsay", '{"message": "Hi there"}')   
    if res.status_code == 200:
        print(res.text)
```

### API methods

#### Cluster methods

**get_cluster_info**
``` python
# get the cluster information
info = client.get_cluster_info() # returns an http response
```

**get_cluster_config**
``` python
# get the cluster config
config = client.get_cluster_config() # returns an http response
```

#### Service methods

**get_service**
``` python
# get the definition of a service 
service = client.get_service("service_name") # returns an http response
```

**list_services**
``` python
# get a list of all the services deployed 
services = client.list_services() # returns an http response
```

> _Note_ : Both `path_to_fdl` and the script path inside the fdl must be absolute.

**create_service**
``` python
# create a service 
err = client.create_service("path_to_fdl") # returns nothing if the service is created or an error if something goes wrong
```

**update_service**
``` python
# update a service 
err = client.update_service("service_name","path_to_fdl") # returns nothing if the service is created or an error if something goes wrong
```

**remove_service**
``` python
# remove a service 
response = client.remove_service("service_name") # returns an http response
```

**run_service**

The `input` parameter may not be passed if the function doesn't require an input.

``` python
# make a synchronous execution 
response = client.run_service("service_name", input="input") # returns an http response

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

You can create a storage object to operate over the different storage providers defined on a service with the method `create_storage_client` as it follows:

``` python
storage_service = client.create_storage_client("service_name") # returns a storage object
```
> _Note_ : The `storage_provider` parameter on the storage methods follows the format: `["storage_provider_type"].["storage_provider_name"]` where `storage_provider_type` is one of the suported storage providers (minIO, S3, Onedata or webdav) and `storage_provider_name` is the identifier _(ex: minio.default)_

**list_files_from_path**

This method returns a json with the info except for Onedata, which returns an http response.

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






