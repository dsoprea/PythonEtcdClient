from etcd.common_ops import CommonOps


class _InOrder(CommonOps):
    """Represents an in-order directory at a specific path.

    :param client: Instance of client
    :param fq_path: Full path of the directory.

    :type client: :class:`etcd.client.Client`
    :type fq_path: string
    """

    def __init__(self, path, *args, **kwargs):
        super(_InOrder, self).__init__(*args, **kwargs)

        self.__path = path

    def create(self):
        """Explicitly create the directory. Not usually necessary.
        :returns: Response object
        :rtype: :class:`etcd.response.ResponseV2`
        """

        return self.client.directory.create(self.__path)

    def delete(self):
        """Delete the directory.
        :returns: Response object
        :rtype: :class:`etcd.response.ResponseV2`
        """

        return self.client.directory.delete_recursive(self.__path)

    def pop(self, name):
        self.client.node.delete(self.__path + '/' + name)

    def add(self, value):
        """Add an in-order value.

        :param value: Value to be automatically-assigned a key.
        :type value: string

        :returns: Response object
        :rtype: :class:`etcd.response.ResponseV2`
        """

# TODO: Can we send a TTL?

        fq_path = self.get_fq_node_path(self.__path)
        return self.client.send(2, 'post', fq_path, value=value)

    def list(self, sorted=False):
        """Return a list of the inserted nodes.

        :param sorted: Return nodes in the proper, chronological order.
        :type sorted: bool

        :returns: Response object
        :rtype: :class:`etcd.response.ResponseV2`
        """

        parameters = {}
        if sorted is True:
            parameters['sorted'] = 'true'

        return self.client.send(2, 'get', self.__path, parameters=parameters)


class InOrderOps(CommonOps):
    """The functions having to do with in-order keys."""

    def get_inorder(self, path):
        """Get an instance of the in-order directory class for a specific key.

        :param path: Key
        :type path: string

        :returns: A _InOrder instance for the given path.
        :rtype: :class:`etcd.inorder_ops._InOrder`
        """

        return _InOrder(path, self.client)
