from etcd.common_ops import CommonOps


class DirectoryOps(CommonOps):
    def __init__(self, client):
        self.__client = client

    def delete(self, path):
        fq_path = self.get_fq_node_path(path)

        parameters = { 'dir': 'true' }
        return self.__client.send(2, 'delete', fq_path, parameters=parameters)

    def delete_recursive(self, path):
        fq_path = self.get_fq_node_path(path)

        parameters = { 'dir': 'true', 'recursive': 'true' }
        return self.__client.send(2, 'delete', fq_path, parameters=parameters)
