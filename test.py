from build.lib.oscar_python.client import Client

"""
options_basic_auth = {'cluster_id':'oscar-cluster-keycloak',
            'endpoint':'https://determined-cray3.im.grycap.net',
            'refresh_token': 'eyJhbGciOiJIUzUxMiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI1OTU3ODBiOC0xYjYxLTRjMjgtOWZjNS1kMGU0ZTg0Yjk0MTgifQ.eyJleHAiOjE3Njg1NDY2MjAsImlhdCI6MTc1OTkwNjYyMCwianRpIjoiMmMzOGFiYWQtYzVhNC00MzM5LTljZjAtY2M1OGNhMDlkNjQ2IiwiaXNzIjoiaHR0cHM6Ly9rZXljbG9hay5ncnljYXAubmV0L3JlYWxtcy9ncnljYXAiLCJhdWQiOiJodHRwczovL2tleWNsb2FrLmdyeWNhcC5uZXQvcmVhbG1zL2dyeWNhcCIsInN1YiI6IjJiZjkyMzU3LThhYTAtNGYyMC1iYjg2LTkyMDdkYzU0MTBhOCIsInR5cCI6IlJlZnJlc2giLCJhenAiOiJvc2Nhci1rZXljbG9hay1jbGllbnQiLCJzaWQiOiIyMGU4OGJiMS04NDA5LTQ0YzEtOTNiNy1kN2VlMmRmMzA0NmQiLCJzY29wZSI6ImVtYWlsIGFjciB3ZWItb3JpZ2lucyByb2xlcyBvcGVuaWQgYmFzaWMgcHJvZmlsZSJ9.t8pu6d0lx7e5rMiIoPBbnbF7-6iXHxS4GxWacB0hYVwu_ttdeGW2cnU2bcpfn_mjeVx56ewj1GZZvG8lNBV2cg',
            'scopes': ["openid", "profile", "email"],
            'token_endpoint': "https://keycloak.grycap.net/realms/grycap/protocol/openid-connect/token",
            'client_id': "oscar-keycloak-client",
            'ssl':'True'}


options_basic_auth = {'cluster_id':'oscar-cluster-egi',
            'endpoint':'https://determined-cray3.im.grycap.net',
            'shortname':'keycloakgrycap',
            'ssl':'True'}
"""
options_basic_auth = {'cluster_id':'oscar-cluster-keycloak',
            'endpoint':'https://determined-cray3.im.grycap.net',
            'shortname':'slangarita',
            'ssl':'True'}

client = Client(options = options_basic_auth)
#services = client.list_services() # returns an http response or an HTTPError
client.create_service("/home/slangarita/Work/oscar/examples/cowsay/cowsay.yaml")
client.remove_service("cowsay")
client.create_service("/home/slangarita/Work/oscar/examples/cowsay/cowsay_abs.yaml")
client.remove_service("cowsay")
client.create_service("../oscar/examples/cowsay/cowsay.yaml")
client.remove_service("cowsay")
#print(services.json())
#jobs= client.list_jobs("grayify","")
#print(jobs.json())

