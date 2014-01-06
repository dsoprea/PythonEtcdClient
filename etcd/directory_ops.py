from etcd.common_ops import CommonOps


class DirectoryOps(CommonOps):
    """Functions specific to directory management.

    :param client: Client instance.
    :type client: :class:`etcd.client.Client`
    """

    def __init__(self, client):
        self.__client = client

    def create(self, path, ttl=None):
        """A normal node-set will implicitly create directories on the way to 
        setting a value. This call exists for when you'd like to -explicitly- 
        create one.

        :param path: Key
        :param ttl: Time until removed

        :type path: string
        :type ttl: int or None

        :returns: Response object
        :rtype: :class:`etcd.response.ResponseV2`
        """

        fq_path = self.get_fq_node_path(path)
        data = { 'dir': 'true' }

        if ttl is not None:
            data['ttl'] = ttl

        return self.__client.send(2, 'put', fq_path, data=data)

    def delete(self, path):
        """Delete the given directory. It must be empty.

        :param path: Key
        :type path: string

        :returns: Response object
        :rtype: :class:`etcd.response.ResponseV2`
        """

        fq_path = self.get_fq_node_path(path)

        parameters = { 'dir': 'true' }
        return self.__client.send(2, 'delete', fq_path, parameters=parameters)

    def delete_recursive(self, path):
        """Delete the given directory, along with any children.

        :param path: Key
        :param ttl: Time until removed

        :type path: string
        :type ttl: int or None

        :returns: Response object
        :rtype: :class:`etcd.response.ResponseV2`
        """

        fq_path = self.get_fq_node_path(path)

        parameters = { 'dir': 'true', 'recursive': 'true' }
        return self.__client.send(2, 'delete', fq_path, parameters=parameters)
