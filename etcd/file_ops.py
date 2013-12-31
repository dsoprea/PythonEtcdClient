from etcd.common_ops import CommonOps
from etcd.response import ResponseV2 


class FileOps(CommonOps):
    def __init__(self, client):
        self.__client = client

    def set(self, path, value):
        self.validate_path(path)

        fq_path = '/keys' + path
        verb = 'put'
        r = self.__client.send(2, verb, fq_path, value)

        return ResponseV2(r, verb, path)
