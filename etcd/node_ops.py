from requests.exceptions import HTTPError
from requests.status_codes import codes

from etcd.exceptions import EtcdPreconditionException
from etcd.common_ops import CommonOps
from etcd.response import ResponseV2 


class NodeOps(CommonOps):
    """Common key-value functions."""

    def get(self, path, recursive=False):
        """Get the given node.

        :param path: Node key
        :type path: string

        :param recursive: Node is a directory, and we want to read it 
                          recursively.
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
            return self.client.send(2, 'get', fq_path, parameters=parameters)
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
        :type path: string

        :param value: Value to assign
        :type value: scalar

        :param ttl: Number of seconds until expiration
        :type ttl: int or None

        :returns: Response object
        :rtype: :class:`etcd.response.ResponseV2`
        """

        fq_path = self.get_fq_node_path(path)
        data = { }

        if ttl is not None:
            data['ttl'] = ttl

        return self.client.send(2, 'put', fq_path, value, data=data)

    def wait(self, path, recursive=False):
        """Long-poll on the given path until it changes.

        :param path: Node key
        :type path: string

        :param recursive: Wait on any change in the given directory or any of 
                          its descendants.
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
            return self.client.send(2, 'get', fq_path, parameters=parameters)
        except HTTPError as e:
            if e.response.status_code == codes.not_found:
                raise KeyError(path)

            raise

    def delete(self, path, current_value=None, current_index=None):
        """Delete the given node.

        :param path: Node key
        :type path: string

        :param current_value: Current value to check
        :type current_value: string or None

        :param current_index: Current index to check
        :type current_index: int or None

        :returns: Response object
        :rtype: :class:`etcd.response.ResponseV2`
        """

        if current_value is not None or current_index is not None:
            return self.compare_and_delete(path, is_dir=False, 
                                           current_value=current_value, 
                                           current_index=current_index)

        fq_path = self.get_fq_node_path(path)
# TODO: If this raises an error for an non-existent key, we'll have to 
#       translate it to a KeyError.
        return self.client.send(2, 'delete', fq_path)

    def delete_if_value(self, path, current_value):
        """Only delete the given node if it's at the given value. 

        :param path: Key
        :type path: string

        :param current_value: Current value to check
        :type current_value: string

        :returns: Response object
        :rtype: :class:`etcd.response.ResponseV2`
        """

        return self.compare_and_delete(path, is_dir=False, 
                                       current_value=current_value)

    def delete_if_index(self, path, current_index):
        """Only delete the given node if it's at the given index. 

        :param path: Key
        :type path: string

        :param current_index: Current index to check
        :type current_index: int or None

        :returns: Response object
        :rtype: :class:`etcd.response.ResponseV2`
        """

        return self.compare_and_delete(path, is_dir=False, 
                                       current_index=current_index)

    def compare_and_swap(self, path, value, current_value=None, 
                         current_index=None, prev_exists=None, ttl=None):
        """The base compare-and-swap function for atomic comparisons. A  
        combination of criteria may be used if necessary.

        :param path: Node key
        :type path: string

        :param value: Value to assign
        :type value: scalar

        :param current_value: Current value to check
        :type current_value: scalar or None

        :param current_index: Current index to check
        :type current_index: int or None

        :param prev_exists: Whether the node should exist or not
        :type prev_exists: bool or None

        :param ttl: The number of seconds until the node expires
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
            return self.client.send(2, 'put', fq_path, value, data=data, 
                                    parameters=parameters)
        except HTTPError as e:
            if e.response.status_code == codes.precondition_failed:
                raise EtcdPreconditionException()

            raise

    def create_only(self, path, value, ttl=None):
        """A convenience function that will only set a node if it doesn't 
        already exist.

        :param path: Node key
        :type path: string

        :param value: Value to assign
        :type value: scalar

        :param ttl: The number of seconds until the node expires
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
        :type path: string

        :param value: Value to assign
        :type value: scalar

        :param ttl: The number of seconds until the node expires
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
        :type path: string

        :param value: Value to assign
        :type value: scalar

        :param current_index: Current index to check
        :type current_index: int

        :param ttl: The number of seconds until the node expires
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
        :type path: string

        :param value: Value to assign
        :type value: scalar

        :param current_value: Current value to check
        :type current_value: scalar or None

        :param ttl: The number of seconds until the node expires
        :type ttl: int or None

        :returns: Response object
        :rtype: :class:`etcd.response.ResponseV2`
        """

        # This will have a return "action" of "compareAndSwap".
        return self.compare_and_swap(path, value, current_value=current_value, ttl=ttl)
