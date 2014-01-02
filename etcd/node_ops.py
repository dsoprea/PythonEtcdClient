from etcd.common_ops import CommonOps
from etcd.response import ResponseV2 


class NodeOps(CommonOps):
    def __init__(self, client):
        self.__client = client

    def get(self, path):
        fq_path = self.get_fq_node_path(path)
        return self.__client.send(2, 'get', fq_path)

    def set(self, path, value, ttl=None):
        fq_path = self.get_fq_node_path(path)
        data = { }

        if ttl is not None:
            data['ttl'] = ttl

        return self.__client.send(2, 'put', fq_path, value, data)

    def delete(self, path):
        fq_path = self.get_fq_node_path(path)
        return self.__client.send(2, 'delete', fq_path)

    def delete(self, path):
        fq_path = self.get_fq_node_path(path)
        return self.__client.send(2, 'delete', fq_path)
