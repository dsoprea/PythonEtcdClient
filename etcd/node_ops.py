import logging

from requests.exceptions import HTTPError, ChunkedEncodingError
from requests.status_codes import codes

import etcd.config

from etcd.exceptions import EtcdPreconditionException, EtcdAtomicWriteError, \
                            translate_exceptions
from etcd.common_ops import CommonOps
from etcd.response import ResponseV2 

_logger = logging.getLogger(__name__)


class NodeOps(CommonOps):
    """Common key-value functions."""

    @translate_exceptions
    def get(self, path, force_consistent=False, force_quorum=False):
        """Get the given node.

        :param path: Node key
        :type path: string

        :param force_consistent: Only interact with the current leader so 
                                 propagation is not a concern.
        :type force_consistent: bool

        :returns: Response object
        :rtype: :class:`etcd.response.ResponseV2`

        :raises: KeyError
        """

        parameters = {}
        if force_consistent is True:
            parameters['consistent'] = 'true'

        if force_quorum is True:
            parameters['quorum'] = 'true'

        fq_path = self.get_fq_node_path(path)
        return self.client.send(2, 'get', fq_path, parameters=parameters)

    @translate_exceptions
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

    @translate_exceptions
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
        return self.client.send(2, 'delete', fq_path)

    @translate_exceptions
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

    @translate_exceptions
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

    @translate_exceptions
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

        return self.client.send(2, 'put', fq_path, value, data=data, 
                                parameters=parameters)

    @translate_exceptions
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

    @translate_exceptions
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

    @translate_exceptions
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

    @translate_exceptions
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

    @translate_exceptions
    def wait(self, path):
        return super(NodeOps, self).wait(path)

    @translate_exceptions
    def atomic_update(self, path, update_value_cb,
                      max_attempts=etcd.config.ATOMIC_MAX_ATTEMPTS, ttl=None):
        """Retrieve the value for the given path, pass it to the callback, get 
        an update value back, and try updating. Loop until the update can be 
        performed atomically.

        :param path: Node key
        :type path: string

        :param update_value_cb: Callback
        :type update_value_cb: callback
        """

        i = max_attempts
        while i > 0:
            response = self.get(path)
            value = update_value_cb(response.node.value)

            try:
                return self.update_if_index(
                        path, 
                        value, 
                        response.node.modified_index, 
                        ttl=ttl)
            except EtcdPreconditionException:
                pass

            i -= 1

        raise EtcdAtomicWriteError("Atomic update failed (%d): %s" % (i, path))
