from etcd.common_ops import CommonOps


class DirectoryOps(CommonOps):
    def __init__(self, client):
        self.__client = client

    def create(self, path, ttl=None):
        fq_path = self.get_fq_node_path(path)
        data = { 'dir': 'true' }

        if ttl is not None:
            data['ttl'] = ttl

        return self.__client.send(2, 'put', fq_path, data=data)

    def delete(self, path):
        fq_path = self.get_fq_node_path(path)

        parameters = { 'dir': 'true' }
        return self.__client.send(2, 'delete', fq_path, parameters=parameters)

    def delete_recursive(self, path):
        fq_path = self.get_fq_node_path(path)

        parameters = { 'dir': 'true', 'recursive': 'true' }
        return self.__client.send(2, 'delete', fq_path, parameters=parameters)
