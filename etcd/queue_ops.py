from etcd.common_ops import CommonOps


class _Queue(object):
    def __init__(self, client, fq_path):
        self.__client = client
        self.__fq_path = fq_path

    def add(self, value):
# TODO: Can we send a TTL?
        return self.__client.send(2, 'post', self.__fq_path, value=value)

    def list(self, sorted=False):
        parameters = {}
# TODO: What does "sorted" do? (it doesn't seem to sort by value, but then what else could it be used for?)
# TODO: What does "recursive" do when sent with a GET on a queue.
        if sorted is True:
            parameters['sorted'] = 'true'

        return self.__client.send(2, 'get', self.__fq_path, 
                                  parameters=parameters)


class QueueOps(CommonOps):
    def __init__(self, client):
        self.__client = client

    def get_queue(self, path):
        fq_path = self.get_fq_node_path(path)
        return _Queue(self.__client, fq_path)
