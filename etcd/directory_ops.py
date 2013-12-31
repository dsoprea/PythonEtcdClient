from etcd.common_ops import CommonOps


class DirectoryOps(CommonOps):
    def __init__(self, client):
        self.__client = client
