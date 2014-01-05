from etcd.common_ops import CommonOps


class _InOrder(object):
    def __init__(self, client, fq_path):
        self.__client = client
        self.__fq_path = fq_path

    def add(self, value):
# TODO: Can we send a TTL?
        return self.__client.send(2, 'post', self.__fq_path, value=value)

    def list(self, sorted=True):
        """Return a list of the queued nodes. Setting "sorted" to True 
        indicates that they will be returned in the proper, chronological 
        order.
        """

        parameters = {}
# TODO: What does "recursive" do when sent with a GET on a queue.
        if sorted is True:
            parameters['sorted'] = 'true'

        return self.__client.send(2, 'get', self.__fq_path, 
                                  parameters=parameters)


class InOrderOps(CommonOps):
    def __init__(self, client):
        self.__client = client

    def get_inorder(self, path):
        fq_path = self.get_fq_node_path(path)
        return _InOrder(self.__client, fq_path)
