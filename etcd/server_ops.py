import requests

from urlparse import parse_qsl

from etcd.common_ops import CommonOps
from etcd.response import ResponseV2 


class ServerOps(CommonOps):
    """Functions that query the server for cluster-level information."""

    def get_version(self):
        """Return a string representing the version of the server that we're 
        connected to.

        :returns: Version
        :rtype: string
        """

        version_string = self.get_text('version', '/version', version=None)

        # Version should look like "etcd v0.2.0".
        prefix = 'etcd v'

        if version_string.startswith(prefix) is False:
            raise ValueError("Could not parse server version: %s" % (r.text))

        return version_string[len(prefix):]

    def get_leader_url_prefix(self):
        """Return the URL prefix of the leader host.

        :returns: URL prefix
        :rtype: string
        """

        return self.get_text('leader', '/leader')

    def get_machines(self):
        """Return the list of servers in the cluster represented as nodes.

        :returns: Response object
        :rtype: :class:`etcd.response.ResponseV2`
        """

        fq_path = self.get_fq_node_path('/_etcd/machines')
        response = self.client.send(2, 'get', fq_path, allow_reconnect=False)

        for machine in response.node.children:
            yield parse_qsl(machine.value)

    def get_dashboard_url(self):
        """Return the URL for the dashboard on the server currently connected-
        to.

        :returns: URL
        :rtype: string
        """

        return (self.client.prefix + '/mod/dashboard')

