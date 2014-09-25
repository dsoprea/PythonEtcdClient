from requests.exceptions import HTTPError
from requests.status_codes import codes

from etcd.exceptions import EtcdAlreadyExistsException, translate_exceptions
from etcd.common_ops import CommonOps

# TODO(dustin): We may need a directory-specific version of 
#               translate_exceptions. We'll see.


class DirectoryOps(CommonOps):
    """Functions specific to directory management."""

    @translate_exceptions
    def list(self, path, recursive=False, force_consistent=False, force_quorum=False):
        """Return a list of the nodes.

        :param recursive: Return all children, and children-of-children.
        :type recursive: bool

        :param force_consistent: Only interact with the current leader so 
                                 propagation is not a concern.
        :type force_consistent: bool

        :returns: Response object
        :rtype: :class:`etcd.response.ResponseV2`
        """

        fq_path = self.get_fq_node_path(path)

        parameters = {}
        if recursive is True:
            parameters['recursive'] = 'true'

        if force_consistent is True:
            parameters['consistent'] = 'true'

        if force_quorum is True:
            parameters['quorum'] = 'true'

        return self.client.send(2, 'get', fq_path, parameters=parameters)

    @translate_exceptions
    def create(self, path, ttl=None):
        """A normal node-set will implicitly create directories on the way to 
        setting a value. This call exists for when you'd like to -explicitly- 
        create one.

        We implicitly fail if the directory already exists.

        :param path: Key
        :type path: string

        :param ttl: Time until removed
        :type ttl: int or None

        :returns: Response object
        :rtype: :class:`etcd.response.ResponseV2`
        :raises: EtcdAlreadyExistsException
        """

        fq_path = self.get_fq_node_path(path)
        data = { 'dir': 'true' }

        if ttl is not None:
            data['ttl'] = ttl

        try:
            return self.client.send(2, 'put', fq_path, data=data)
        except HTTPError as e:
            if e.response.status_code == codes.forbidden:
                try:
                    j = e.response.json()
                except ValueError:
                    pass
                else:
# TODO(dustin): Complain about this error message.
                    # "message" == "Not a file"
                    if j['errorCode'] == 102:
                        raise EtcdAlreadyExistsException(path)

            raise

    @translate_exceptions
    def delete(self, path, current_value=None, current_index=None):
        """Delete the given directory. It must be empty.

        :param path: Key
        :type path: string

        :param current_index: Current index to check
        :type current_index: int or None

        :returns: Response object
        :rtype: :class:`etcd.response.ResponseV2`
        """

        if current_index is not None:
            return self.compare_and_delete(path, is_dir=True, 
                                           current_index=current_index)

        fq_path = self.get_fq_node_path(path)

        parameters = { 'dir': 'true' }
        return self.client.send(2, 'delete', fq_path, parameters=parameters)

    @translate_exceptions
    def delete_if_index(self, path, current_index):
        """Only delete the given directory if the node is at the given index. 
        It must be empty.

        :param path: Key
        :type path: string

        :param current_index: Current index to check
        :type current_index: int or None

        :returns: Response object
        :rtype: :class:`etcd.response.ResponseV2`
        """

        return self.compare_and_delete(path, is_dir=True, 
                                       current_index=current_index)

    @translate_exceptions
    def delete_recursive(self, path, current_index=None):
        """Delete the given directory, along with any children.

        :param path: Key
        :type path: string

        :param current_index: Current index to check
        :type current_index: int or None

        :returns: Response object
        :rtype: :class:`etcd.response.ResponseV2`
        """

        if current_index is not None:
            return self.compare_and_delete(path, is_recursive=True,
                                           current_index=current_index)

        fq_path = self.get_fq_node_path(path)

        parameters = { 'dir': 'true', 'recursive': 'true' }
        return self.client.send(2, 'delete', fq_path, parameters=parameters)

    @translate_exceptions
    def delete_recursive_if_index(self, path, current_index):
        """Only delete the given directory (and its children) if the node is at 
        the given index. 

        :param path: Key
        :type path: string

        :param current_index: Current index to check
        :type current_index: int or None

        :returns: Response object
        :rtype: :class:`etcd.response.ResponseV2`
        """

        return self.compare_and_delete(path, is_recursive=True, 
                                       current_index=current_index)
