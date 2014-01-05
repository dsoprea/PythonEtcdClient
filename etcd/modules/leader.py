from requests.exceptions import HTTPError

from etcd.common_ops import CommonOps


class LeaderMod(CommonOps):
    """'Leader' functionality for consensus-based assignment. If multiple 
    processes try to assign different simple strings to the given key, the 
    first will succeed and block the others until the TTL expires. The same 
    process repeats for all subsequent assignments.
    """

    def __init__(self, client):
        self.__client = client

    def __get_path(self, leader_key):
        return ('/' + leader_key)

    def set_or_renew(self, key, value, ttl):
        self.__client.debug("LEADER: Setting key [%s] with value [%s]." % 
                            (key, value))

        fq_path = self.__get_path(key)

# TODO: Why is it called "name"?
        data = { 'name': value }
        parameters = { 'ttl': ttl }

        self.__client.send(2, 'put', fq_path, data=data, 
                           parameters=parameters, module='leader', 
                           return_raw=True)

    def get(self, key):
        self.__client.debug("LEADER: Getting value for key [%s]." % (key))

        fq_path = self.__get_path(key)

# TODO: 
#
# If this fails, we get a text response on a 200:
#
#       get leader error: read lock error: Cannot reach servers after 3 time\n
#
# Raise a KeyError when this is fixed.

        r = self.__client.send(2, 'get', fq_path, module='leader', 
                               return_raw=True)

        if r.text == '':
            return None

        result = r.text
        if result.startswith('get leader error:') is True:
            raise KeyError(key)

        return result

    def delete(self, key, value):
        self.__client.debug("LEADER: Deleting key [%s] with value [%s]." % 
                            (key, value))

# TODO: 
#
# If this fails, we get a text response with a 500: 
#
#       delete leader error: release lock error: cannot find: test value
#
# Raise a KeyError when this is fixed.

        fq_path = self.__get_path(key)
        parameters = { 'name': value }

        try:
            self.__client.send(2, 'delete', fq_path, module='leader', 
                               parameters=parameters, return_raw=True)
        except HTTPError as e:
            if e.response.status_code == 500:
                raise KeyError(key)

            raise
