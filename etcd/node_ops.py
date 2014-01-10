from requests.exceptions import HTTPError
from requests.status_codes import codes

from etcd.exceptions import EtcdPreconditionException
from etcd.common_ops import CommonOps
from etcd.response import ResponseV2 


class NodeOps(CommonOps):
    """Common key-value functions."""
# TODO: Add doc for constructor.
    def __init__(self, client):
        self.__client = client

    def get(self, path, recursive=False):
        """Get the given node.

        :param path: Node key
        :param recursive: Node is a directory, and we want to read it 
                          recursively.
        :type path: string
        :type recursive: bool

        :returns: Response object
        :rtype: :class:`etcd.response.ResponseV2`

        :raises: KeyError
        """

        fq_path = self.get_fq_node_path(path)

        parameters = { }

        if recursive is True:
            parameters['recursive'] = 'true'

        try:
            return self.__client.send(2, 'get', fq_path, parameters=parameters)
        except HTTPError as e:
            if e.response.status_code == codes.not_found:
                try:
                    j = e.response.json()
                except ValueError:
                    pass
                else:
                    if j['errorCode'] == 100:
                        raise KeyError(path)

            raise

    def set(self, path, value, ttl=None):
        """Set the given node.

        :param path: Node key
        :param value: Value to assign
        :param ttl: Number of seconds until expiration

        :type path: string
        :type value: scalar
        :type ttl: int or None

        :returns: Response object
        :rtype: :class:`etcd.response.ResponseV2`
        """

        fq_path = self.get_fq_node_path(path)
        data = { }

        if ttl is not None:
            data['ttl'] = ttl

        return self.__client.send(2, 'put', fq_path, value, data=data)
# TODO: Doc this in README.
    def wait(self, path, recursive=False):
        """Long-poll on the given path until it changes.

        :param path: Node key
        :param recursive: Wait on any change in the given directory or any of 
                          its descendants.

        :type path: string
        :type recursive: bool

        :returns: Response object
        :rtype: :class:`etcd.response.ResponseV2`

        :raises: KeyError
        """

        fq_path = self.get_fq_node_path(path)

        parameters = { 'wait': 'true' }

        if recursive is True:
            parameters['recursive'] = 'true'

        try:
            return self.__client.send(2, 'get', fq_path, parameters=parameters)
        except HTTPError as e:
            if e.response.status_code == codes.not_found:
                raise KeyError(path)

            raise

    def delete(self, path):
        """Delete the given node.

        :param path: Node key
        :type path: string

        :returns: Response object
        :rtype: :class:`etcd.response.ResponseV2`
        """

        fq_path = self.get_fq_node_path(path)
# TODO: If this raises an error for an non-existent key, we'll have to 
#       translate it to a KeyError.
        return self.__client.send(2, 'delete', fq_path)

    def compare_and_swap(self, path, value, current_value=None, 
                         current_index=None, prev_exists=None, ttl=None):
        """The base compare-and-swap function for atomic comparisons. A  
        combination of criteria may be used if necessary.

        :param path: Node key
        :param value: Value to assign
        :param current_value: Current value to check
        :param current_index: Current index to check
        :param prev_exists: Whether the node should exist or not
        :param ttl: The number of seconds until the node expires

        :type path: string
        :type value: scalar
        :type current_value: scalar or None
        :type current_index: int or None
        :type prev_exists: bool or None
        :type ttl: int or None

        :returns: Response object
        :rtype: :class:`etcd.response.ResponseV2`

        :raises: :class:`etcd.exceptions.EtcdPreconditionException`
        """

        fq_path = self.get_fq_node_path(path)

        parameters = {}
        data = { }

        if current_value is not None:
            parameters['prevValue'] = current_value

        if current_index is not None:
            parameters['prevIndex'] = current_index

        if prev_exists is not None:
            parameters['prevExist'] = 'true' if prev_exists is True \
                                             else 'false'

        if not parameters:
            return self.set(path, value, ttl=ttl)

        if ttl is not None:
            data['ttl'] = ttl

        try:
            return self.__client.send(2, 'put', fq_path, value, data=data, 
                                      parameters=parameters)
        except HTTPError as e:
            if e.response.status_code == codes.precondition_failed:
                raise EtcdPreconditionException()

            raise

    def create_only(self, path, value, ttl=None):
        """A convenience function that will only set a node if it doesn't 
        already exist.

        :param path: Node key
        :param value: Value to assign
        :param ttl: The number of seconds until the node expires

        :type path: string
        :type value: scalar
        :type ttl: int or None

        :returns: Response object
        :rtype: :class:`etcd.response.ResponseV2`
        """

        # This will have a return "action" of "create".
        return self.compare_and_swap(path, value, prev_exists=False, ttl=ttl)

    def update_only(self, path, value, ttl=None):
        """A convenience function that will only set a node if it already
        exists.

        :param path: Node key
        :param value: Value to assign
        :param ttl: The number of seconds until the node expires

        :type path: string
        :type value: scalar
        :type ttl: int or None

        :returns: Response object
        :rtype: :class:`etcd.response.ResponseV2`
        """

        # This will have a return "action" of "update".
        return self.compare_and_swap(path, value, prev_exists=True, ttl=ttl)

    def update_if_index(self, path, value, current_index, ttl=None):
        """A convenience function that will only set a node if its existing
        "modified index" matches.

        :param path: Node key
        :param value: Value to assign
        :param current_index: Current index to check
        :param ttl: The number of seconds until the node expires

        :type path: string
        :type value: scalar
        :type current_index: int
        :type ttl: int or None

        :returns: Response object
        :rtype: :class:`etcd.response.ResponseV2`
        """

        # This will have a return "action" of "compareAndSwap".
        return self.compare_and_swap(path, value, current_index=current_index, ttl=ttl)

    def update_if_value(self, path, value, current_value, ttl=None):
        """A convenience function that will only set a node if its existing value
        matches.

        :param path: Node key
        :param value: Value to assign
        :param current_value: Current value to check
        :param ttl: The number of seconds until the node expires

        :type path: string
        :type value: scalar
        :type current_value: scalar or None
        :type ttl: int or None

        :returns: Response object
        :rtype: :class:`etcd.response.ResponseV2`
        """

        # This will have a return "action" of "compareAndSwap".
        return self.compare_and_swap(path, value, current_value=current_value, ttl=ttl)
