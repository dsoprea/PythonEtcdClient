import requests

from os import environ

from etcd.config import DEFAULT_HOSTNAME, DEFAULT_PORT, DEFAULT_SCHEME
from etcd.directory_ops import DirectoryOps
from etcd.node_ops import NodeOps
from etcd.server_ops import ServerOps
from etcd.inorder_ops import InOrderOps
from etcd.modules.lock import LockMod
from etcd.modules.leader import LeaderMod
from etcd.response import ResponseV2

# TODO: Add support for SSL: 
#   curl --key ./fixtures/ca/server2.key.insecure --cert ./fixtures/ca/server2.crt --cacert ./fixtures/ca/server-chain.pem -L https://127.0.0.1:4001/v2/keys/foo -XPUT -d value=bar -v


class _Modules(object):
    def __init__(self, client):
        self.__client = client

    @property
    def lock(self):
        try:
            return self.__lock
        except AttributeError:
            self.__lock = LockMod(self.__client)
            return self.__lock

    @property
    def leader(self):
        try:
            return self.__leader
        except AttributeError:
            self.__leader = LeaderMod(self.__client)
            return self.__leader


class Client(object):
    def __init__(self, hostname=DEFAULT_HOSTNAME, port=DEFAULT_PORT, scheme=DEFAULT_SCHEME, debug=False):
        debug_override = environ.get('ETCD_DEBUG')
        if debug_override is not None and debug_override == 'true':
            debug = True

        self.__debug = debug

        self.__hostname = hostname
        self.__port = port
        self.__scheme = scheme

        self.__prefix = ('%s://%s:%s' % (scheme, hostname, port))
        self.debug("PREFIX= [%s]" % (self.__prefix))

# TODO: Remove the version check after debugging.
# TODO: Can we implicitly read the version from the response/headers?
        self.__version = self.server.get_version()
        self.debug("Version: %s" % (self.__version))

        if self.__version.startswith('0.2') is False:
            raise ValueError("We don't support an etcd version older than 0.2.0 .")

    def __str__(self):
        return ('<ETCD %s>' % (self.__prefix))

    def debug(self, message):
        if self.__debug is True:
            print("EC: %s" % (message))

    def send(self, version, verb, path, value=None, parameters=None, data=None, module=None, return_raw=False):
        if parameters is None:
            parameters = {}

        if data is None:
            data = {}

        if version != 2:
            raise ValueError("We were told to send a version (%d) request, "
                             "which is not supported." % (version))
        else:
            response_cls = ResponseV2

        send = getattr(requests, verb)

        if module is None:
            url = ('%s/v%d%s' % (self.__prefix, version, path))
        else:
            url = ('%s/mod/v%d/%s%s' % (self.__prefix, version, module, path))

        if value is not None:
            data['value'] = value

        args = { 'params': parameters, 'data': data }

        self.debug("Request(%s)=[%s] params=[%s] data_keys=[%s]" % 
                   (verb, url, parameters, args['data'].keys()))

        r = send(url, **args)
        r.raise_for_status()

        if return_raw is True:
            return r

        return response_cls(r, verb, path)

    @property
    def prefix(self):
        return self.__prefix

    @property
    def directory(self):
        try:
            return self.__directory
        except AttributeError:
            self.__directory = DirectoryOps(self)
            return self.__directory

    @property
    def node(self):
        try:
            return self.__node
        except AttributeError:
            self.__node = NodeOps(self)
            return self.__node

    @property
    def server(self):
        try:
            return self.__server
        except AttributeError:
            self.__server = ServerOps(self)
            return self.__server

    @property
    def inorder(self):
        try:
            return self.__inorder
        except AttributeError:
            self.__inorder = InOrderOps(self)
            return self.__inorder

    @property
    def module(self):
        try:
            return self.__module
        except AttributeError:
            self.__module = _Modules(self)
            return self.__module
