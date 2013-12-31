import requests

from etcd.common_ops import CommonOps
from etcd.response import ResponseV2 


class ServerOps(CommonOps):
    def __init__(self, client):
        self.__client = client

    def __get_get_text(self, path, version=2):
        r = requests.get('%s/v%d%s' % (self.__client.prefix, version, path))
        r.raise_for_status()

        return r.text

    def get_server_version(self):
        version_string = self.__get_get_text('/version')

        # Version should look like "etcd v0.2.0".
        if version_string.startswith('etcd v') is False:
            raise ValueError("Could not parse server version: %s" % (r.text))

        return version_string[6:]

    def get_leader_url_prefix(self):
        return self.__get_get_text('/leader')

    def get_machines(self):
        path = '/keys/_etcd/machines'
        verb = 'get'
        r = self.__client.send(2, verb, path)

        return ResponseV2(r, verb, path)

    def get_dashboard_url(self):
        return (self.__client.prefix + '/mod/dashboard/')

# TODO: Add methods for modules: locking, leader election
