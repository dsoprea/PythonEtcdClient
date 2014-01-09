import requests

from urlparse import parse_qsl

from etcd.common_ops import CommonOps
from etcd.response import ResponseV2 


class ServerOps(CommonOps):
    """Functions that query the server for cluster-level information.

    :param client: Client instance
    :type client: :class:`etcd.client.Client`
    """

    def __init__(self, client):
        self.__client = client

    def __get_get_text(self, reason, path, version=2):
        """Execute a request that will return flat text.

        :param reason: Brief phrase describing the request
        :param path: URL path
        :param version: API version

        :type reason: string
        :type path: string
        :type version: int

        :returns: Response text
        :rtype: string
        """

        if version is not None:
            url = ('%s/v%d%s' % (self.__client.prefix, version, path))
        else:
            url = ('%s%s' % (self.__client.prefix, path))

        self.__client.debug("TEXT URL (%s) = [%s]" % (reason, url))

        r = self.__client.session.get(url)
        r.raise_for_status()

        return r.text

    def get_version(self):
        """Return a string representing the version of the server that we're 
        connected to.

        :returns: Version
        :rtype: string
        """

        version_string = self.__get_get_text('version', '/version', version=None)

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

        return self.__get_get_text('leader', '/leader')

    def get_machines(self):
        """Return the list of servers in the cluster represented as nodes.

        :returns: Response object
        :rtype: :class:`etcd.response.ResponseV2`
        """

        fq_path = self.get_fq_node_path('/_etcd/machines')
        response = self.__client.send(2, 'get', fq_path, allow_reconnect=False)

        for machine in response.node.children:
            yield parse_qsl(machine.value)

    def get_dashboard_url(self):
        """Return the URL for the dashboard on the server currently connected-
        to.

        :returns: URL
        :rtype: string
        """

        return (self.__client.prefix + '/mod/dashboard')
