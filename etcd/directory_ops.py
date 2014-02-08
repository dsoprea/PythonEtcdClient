from requests.exceptions import HTTPError
from requests.status_codes import codes

from etcd.exceptions import EtcdAlreadyExistsException
from etcd.common_ops import CommonOps


class DirectoryOps(CommonOps):
    """Functions specific to directory management."""

    def create(self, path, ttl=None):
        """A normal node-set will implicitly create directories on the way to 
        setting a value. This call exists for when you'd like to -explicitly- 
        create one.

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

    def delete_recursive(self, path, current_index=None):
        """Delete the given directory, along with any children.

        :param path: Key
        :type path: string

        :param current_index: Current index to check
        :type current_index: int or None

        :returns: Response object
        :rtype: :class:`etcd.response.ResponseV2`
        """

        if current_value is not None or current_index is not None:
            return self.compare_and_delete(path, is_recursive=True,
                                           current_index=current_index)

        fq_path = self.get_fq_node_path(path)

        parameters = { 'dir': 'true', 'recursive': 'true' }
        return self.client.send(2, 'delete', fq_path, parameters=parameters)

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

