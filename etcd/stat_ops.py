import requests

from urlparse import parse_qsl

from etcd.common_ops import CommonOps
from etcd.response import ResponseV2 


class StatOps(CommonOps):
    """Functions that query the server for statistics information."""

    def get_leader_stats(self):
        """Returns leader and follower information.

        :returns: Tuple of (<leader_name>, { <follower 1>: <stats>, ...})
        :rtype: tuple
        """
        
        r = self.client.send(2, 'get', '/stats/leader', return_raw=True)
        data = r.json()

        return (data['leader'], data['followers'])

    def get_self_stats(self):
        """Returns stats regarding the current node.

        :returns: Statistics data
        :rtype: dict
        """
        
        r = self.client.send(2, 'get', '/stats/self', return_raw=True)
        data = r.json()

        return data

