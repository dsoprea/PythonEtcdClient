import requests

from etcd.config import DEFAULT_HOSTNAME, DEFAULT_PORT, DEFAULT_SCHEME
from etcd.exceptions import EtcdHttpNotFoundException
from etcd.directory_ops import DirectoryOps
from etcd.file_ops import FileOps
from etcd.server_ops import ServerOps
from etcd.lock_ops import LockOps
from etcd.response import ResponseV2

# TODO: Add support for SSL: 
#   curl --key ./fixtures/ca/server2.key.insecure --cert ./fixtures/ca/server2.crt --cacert ./fixtures/ca/server-chain.pem -L https://127.0.0.1:4001/v2/keys/foo -XPUT -d value=bar -v



class Client(object):
    def __init__(self, hostname=DEFAULT_HOSTNAME, port=DEFAULT_PORT, scheme=DEFAULT_SCHEME):
        self.__hostname = hostname
        self.__port = port
        self.__scheme = scheme

        self.__prefix = ('%s://%s:%s' % (scheme, hostname, port))
        self.__version = self.__get_server_version()

        if self.__version.startswith('0.2') is False:
            raise ValueError("We don't support an etcd version older than 0.2.0 .")

    def send(self, version, verb, path, value=None, parameters={}, data={}, module=None, return_raw=False):
        if version != 2:
            raise ValueError("We were told to send a version (%d) request, "
                             "which is not supported." % (version))
        else
            response_cls = ResponseV2

        send = getattr(requests, verb)

        if module is None:
            url = ('%s/v%d%s' % (self.__prefix, version, path))
        else:
            url = ('%s/mod/v%d/%s%s' % (self.__prefix, version, module, path))

        args = { 'params': parameters, 'data': data }
        if value is not None:
            args['data']['value'] = value

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
    def file(self):
        try:
            return self.__file
        except AttributeError:
            self.__file = FileOps(self)
            return self.__file

    @property
    def server(self):
        try:
            return self.__server
        except AttributeError:
            self.__server = ServerOps(self)
            return self.__server

    @property
    def lock(self):
        try:
            return self.__lock
        except AttributeError:
            self.__lock = LockOps(self)
            return self.__lock
