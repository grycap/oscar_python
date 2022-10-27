## Python OSCAR API

### Sample usage

``` python
from oscar_python.client import Client

client = Client("cluster-id","https://cluster-endpoint", "username", "password", True)

# get the cluster information
info = client.get_cluster_info() # returns an http response
print(info.text)
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
service = client.remove_service("service_name") # returns an http response
```

#TODO [...]





