from requests.exceptions import HTTPError
from requests.status_codes import codes

from etcd.exceptions import EtcdPreconditionException
from etcd.common_ops import CommonOps
from etcd.response import ResponseV2 


class NodeOps(CommonOps):
    def __init__(self, client):
        self.__client = client

    def get(self, path, recursive=False):
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
        fq_path = self.get_fq_node_path(path)
        data = { }

        if ttl is not None:
            data['ttl'] = ttl

        return self.__client.send(2, 'put', fq_path, value, data=data)

    def wait(self, path, recursive=False):
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
        fq_path = self.get_fq_node_path(path)
        return self.__client.send(2, 'delete', fq_path)

    def compare_and_swap(self, path, value, current_value=None, 
                         current_index=None, prev_exists=None, ttl=None):
        """The base compare-and-swap function for atomic comparisons. Multiple 
        criteria may be used if necessary.
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
        # This will have a return "action" of "create".
        return self.compare_and_swap(path, value, prev_exists=False, ttl=ttl)

    def update_only(self, path, value, ttl=None):
        # This will have a return "action" of "update".
        return self.compare_and_swap(path, value, prev_exists=True, ttl=ttl)

    def update_if_index(self, path, value, current_index, ttl=None):
        # This will have a return "action" of "compareAndSwap".
        return self.compare_and_swap(path, value, current_index=current_index, ttl=ttl)

    def update_if_value(self, path, value, current_value, ttl=None):
        # This will have a return "action" of "compareAndSwap".
        return self.compare_and_swap(path, value, current_value=current_value, ttl=ttl)
