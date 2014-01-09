import requests
import ssl

from os import environ
from requests.exceptions import ConnectionError
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
from datetime import datetime

from etcd.config import HOST_FAIL_WAIT_S
from etcd.directory_ops import DirectoryOps
from etcd.node_ops import NodeOps
from etcd.server_ops import ServerOps
from etcd.inorder_ops import InOrderOps
from etcd.modules.lock import LockMod
from etcd.modules.leader import LeaderMod
from etcd.response import ResponseV2


class _Ssl3HttpAdapter(HTTPAdapter):
    """"Transport adapter" that allows us to use SSLv3."""

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_SSLv3)


class _Modules(object):
    """Intermediate container that holds functionality related to modules.

    :param client: Client instance
    :type client: :class:`etcd.client.Client`
    """

    def __init__(self, client):
        self.__client = client

    @property
    def lock(self):
        """Return an instance of the class having the lock functionality.

        :rtype: :class:`etcd.response.ResponseV2`
        """

        try:
            return self.__lock
        except AttributeError:
            self.__lock = LockMod(self.__client)
            return self.__lock

    @property
    def leader(self):
        """Return an instance of the class having the leader-election 
        functionality.

        :rtype: :class:`etcd.modules.leader.LeaderMod`
        """

        try:
            return self.__leader
        except AttributeError:
            self.__leader = LeaderMod(self.__client)
            return self.__leader


class Client(object):
    """The main channel of functionality for the client. Connects to the 
    server, and provides functions via properties.

    :param host: Hostname or IP of server
    :param port: Port of server
    :param is_ssl: Whether to use 'http://' or 'https://'.
    :param debug: Whether to print debug verbosity (can be provided as the 
                  ETCD_DEBUG environment variable, as well)
    :param ssl_do_verify: Whether to verify the certificate hostname.
    :param ssl_ca_bundle_filepath: A bundle of rootCAs for verifications.
    :param ssl_client_cert_filepath: A client certificate, for authentication.
    :param ssl_client_key_filepath: A client key, for authentication.

    :type host: string
    :type port: int
    :type is_ssl: bool
    :type debug: bool
    :type ssl_do_verify: bool or None
    :type ssl_ca_bundle_filepath: string or None
    :type ssl_client_cert_filepath: string or None
    :type ssl_client_key_filepath: string or None

    :raises: ValueError
    """

    def __init__(self, host='127.0.0.1', port=4001, 
                 is_ssl=False, debug=None, ssl_do_verify=None, 
                 ssl_ca_bundle_filepath=None, ssl_client_cert_filepath=None,
                 ssl_client_key_filepath=None):
        if debug is None:
            debug = bool(int(environ.get('PEC_DEBUG', '0')))

        self.__debug = debug

        # These are set from the parameters.
        self.__ssl_config_do_verify = ssl_do_verify
        self.__ssl_config_ca_bundle_filepath = ssl_ca_bundle_filepath
        self.__ssl_config_client_cert_filepath = ssl_client_cert_filepath
        self.__ssl_config_client_key_filepath = ssl_client_key_filepath

        # These are set from the processing of SSL configuration.
        self.__ssl_verify = None
        self.__ssl_cert = None

        scheme = 'http' if is_ssl is False else 'https'
        self.__prefix = ('%s://%s:%s' % (scheme, host, port))
        self.debug("PREFIX= [%s]" % (self.__prefix))

        self.__collect_ssl_config()

        self.__session = requests.Session()
        self.__session.mount('https://', _Ssl3HttpAdapter())

# TODO: Remove the version check after debugging.
# TODO: Can we implicitly read the version from the response/headers?
#        self.__version = self.server.get_version()
#        self.debug("Version: %s" % (self.__version))
#
#        if self.__version.startswith('0.2') is False:
#            raise ValueError("We don't support an etcd version older than 0.2.0 .")

        self.__machines = [[dict(machine_info)['etcd'], None]
                            for machine_info
                            in self.server.get_machines()]

        self.debug("Cluster machines: %s" % (self.__machines))

        # This will fail if the given server does appear in the published list 
        # of servers. This might only happen because of a hostname being used 
        # instead of an IP, or vice-versa.
        self.__machine_index = None
        i = 0
        for (prefix, last_fail_dt) in self.__machines:
            if prefix == self.__prefix:
                self.__machine_index = i
                break

            i += 1

        if self.__machine_index is None:
            raise ValueError("Could not identify given prefix [%s] among "
                             "published prefixes: %s" % 
                             (self.__prefix, self.__machines))

        self.debug("The initial machine is at index (%d)." % 
                   (self.__machine_index))

    def __str__(self):
        return ('<ETCD %s>' % (self.__prefix))

    def __collect_ssl_config(self):
        verify = None
        cert = None

        if self.__ssl_config_do_verify is not None:
            verify = 1 if self.__ssl_config_do_verify is True else 0
        else:
            verify = environ.get('PEC_SSL_DO_VERIFY')
            
        if self.__ssl_config_ca_bundle_filepath is not None:
            ca_bundle_filepath = self.__ssl_config_ca_bundle_filepath
        else:
            ca_bundle_filepath = environ.get('PEC_SSL_CA_BUNDLE_FILEPATH')

        if verify is not None:
            verify = bool(int(verify))
        elif ca_bundle_filepath is not None:
            verify = ca_bundle_filepath
        else:
            verify = True

        cert = None
        if self.__ssl_config_client_cert_filepath is not None:
            client_cert_filepath = self.__ssl_config_client_cert_filepath
        else:
            client_cert_filepath = environ.get('PEC_SSL_CLIENT_CERT_FILEPATH')
        
        if client_cert_filepath is not None:
            if self.__ssl_config_client_key_filepath is not None:
                client_key_filepath = self.__ssl_config_client_key_filepath
            else:
                client_key_filepath = environ.get(
                                        'PEC_SSL_CLIENT_KEY_FILEPATH')
            
            if client_key_filepath is not None:
                cert = (client_cert_filepath, client_key_filepath)
            else:
                cert = client_cert_filepath

        if verify is not None or cert is not None:
            self.debug("SSL: verify=[%s] cert=[%s]" % (verify, cert))

        self.__ssl_verify = verify
        self.__ssl_cert = cert

    def debug(self, message):
        """Print a debug message during debug mode.

        :param message: Message to print
        :type message: string
        """

        if self.__debug is True:
            print("EC: %s" % (message))

    def send(self, version, verb, path, value=None, parameters=None, data=None, 
             module=None, return_raw=False, allow_reconnect=True):
        """Build and execute a request.

        :param version: Version of API
        :param verb: Verb of request ('get', 'post', etc..)
        :param path: URL path
        :param value: Value to be converted to string and passed as "value" in 
                      the POST data.
        :param parameters: Dictionary of values to be passed via URL query.
        :param data: Dictionary of values to be passed via POST data.
        :param module: Name of the etcd module that hosts the functionality.
        :param return_raw: Whether to return a 
                           :class:`etcd.response.ResponseV2` object or the raw 
                           Requests response.
        :param allow_reconnect: Allow the client to consider alternate hosts if
                                the current host fails connection.

        :type version: int
        :type verb: string
        :type path: string
        :type value: scalar or None
        :type parameters: dictionary or None
        :type data: dictionary or None
        :type module: string or None
        :type return_raw: bool
        :type allow_reconnect: bool

        :returns: Response object
        :rtype: :class:`etcd.response.ResponseV2`
        """

        if parameters is None:
            parameters = {}

        if data is None:
            data = {}

        if version != 2:
            raise ValueError("We were told to send a version (%d) request, "
                             "which is not supported." % (version))
        else:
            response_cls = ResponseV2

        if module is None:
            url = ('%s/v%d%s' % (self.__prefix, version, path))
        else:
            url = ('%s/mod/v%d/%s%s' % (self.__prefix, version, module, path))

        if value is not None:
            data['value'] = value

        args = { 'params': parameters, 
                 'data': data, 
                 'verify': self.__ssl_verify, 
                 'cert': self.__ssl_cert }

        self.debug("Request(%s)=[%s] params=[%s] data_keys=[%s]" % 
                   (verb, url, parameters, args['data'].keys()))

        send = getattr(self.__session, verb)
    
        while 1:
            try:
                r = send(url, **args)
            except ConnectionError as e:
                self.debug("Connection error with [%s] [%s]: %s" % 
                           (self.__prefix, e.__class__.__name__, str(e)))

                if allow_reconnect is False:
                    raise
            else:
                break

            # If we get here, there was a connection problem. Rotate the server 
            # that we're using, excluding any that have recently failed.

            now_dt = datetime.now()
            self.__machines[self.__machine_index][1] = now_dt

            len_ = len(self.__machines)
            i = 0
            elected = None
            while i < len_:
                machine_index = (self.__machine_index + 1) % len_
                (prefix, last_fail_dt) = self.__machines[machine_index]

                if last_fail_dt is None or \
                   (now_dt - last_fail_dt).total_seconds() > \
                        HOST_FAIL_WAIT_S:
                    elected = prefix

                i += 1

            if elected is None:
                raise SystemError("All servers have failed: %s" % 
                                  (self.__machines,))

            self.__prefix = elected
            self.__machine_index = machine_index

            self.debug("Retrying with next machine: %s" % (self.__prefix))

        r.raise_for_status()

        if return_raw is True:
            return r

        return response_cls(r, verb, path)

    @property
    def session(self):
        return self.__session

    @property
    def prefix(self):
        """Return the URL prefix for the server.

        :rtype: string
        """

        return self.__prefix

    @property
    def directory(self):
        """Return an instance of the class having the directory functionality.

        :rtype: :class:`etcd.directory_ops.DirectoryOps`
        """

        try:
            return self.__directory
        except AttributeError:
            self.__directory = DirectoryOps(self)
            return self.__directory

    @property
    def node(self):
        """Return an instance of the class having the general node 
        functionality.

        :rtype: :class:`etcd.node_ops.NodeOps`
        """

        try:
            return self.__node
        except AttributeError:
            self.__node = NodeOps(self)
            return self.__node

    @property
    def server(self):
        """Return an instance of the class having the server functionality.

        :rtype: :class:`etcd.server_ops.ServerOps`
        """

        try:
            return self.__server
        except AttributeError:
            self.__server = ServerOps(self)
            return self.__server

    @property
    def inorder(self):
        """Return an instance of the class having the "in-order keys" 
        functionality.

        :rtype: :class:`etcd.inorder_ops.InOrderOps`
        """

        try:
            return self.__inorder
        except AttributeError:
            self.__inorder = InOrderOps(self)
            return self.__inorder

    @property
    def module(self):
        """Return an instance of the class that hosts the functionality 
        provided by individual modules.

        :rtype: :class:`etcd.client._Modules`
        """

        try:
            return self.__module
        except AttributeError:
            self.__module = _Modules(self)
            return self.__module
