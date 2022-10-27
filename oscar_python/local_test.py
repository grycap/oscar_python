from client import Client

client = Client("oscar-gpu-cluster","https://focused-boyd8.im.grycap.net", "oscar", "oscar123", True)

res = client.remove_service("cowsay")
if res:
    print(res.status_code)
    print(res.content)
else:
    print("empty")