from etcd.common_ops import CommonOps


class _InOrder(object):
    """Represents an in-order directory at a specific path.

    :param client: Instance of client
    :param fq_path: Full path of the directory.

    :type client: :class:`etcd.client.Client`
    :type fq_path: string
    """

    def __init__(self, client, fq_path):
        self.__client = client
        self.__fq_path = fq_path

    def add(self, value):
        """Add an in-order value.

        :param value: Value to be automatically-assigned a key.
        :type value: string

        :returns: Response object
        :rtype: :class:`etcd.response.ResponseV2`
        """

# TODO: Can we send a TTL?
        return self.__client.send(2, 'post', self.__fq_path, value=value)

    def list(self, sorted=True):
        """Return a list of the inserted nodes.

        :param sorted: Return nodes in the proper, chronological order.
        :type sorted: bool

        :returns: Response object
        :rtype: :class:`etcd.response.ResponseV2`
        """

        parameters = {}
        if sorted is True:
            parameters['sorted'] = 'true'

        return self.__client.send(2, 'get', self.__fq_path, 
                                  parameters=parameters)


class InOrderOps(CommonOps):
    """The functions having to do with in-order keys.

    :param client: Client instance
    :type client: :class:`etcd.client.Client`
    """

    def __init__(self, client):
        self.__client = client

    def get_inorder(self, path):
        """Get an instance of the in-order directory class for a specific key.

        :param path: Key
        :type path: string

        :returns: A _InOrder instance for the given path.
        :rtype: :class:`etcd.inorder_ops._InOrder`
        """

        fq_path = self.get_fq_node_path(path)
        return _InOrder(self.__client, fq_path)
