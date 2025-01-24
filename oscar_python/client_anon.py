from oscar_python.default_client import DefaultClient


class AnonymousClient(DefaultClient):
    # Cluster info
    def __init__(self, options) -> None:
        self.id = options['cluster_id']
        self.endpoint = options["endpoint"]
        self.ssl = bool(options['ssl'])
        self._AUTH_TYPE = "anon"
