import requests

from requests.status_codes import codes
from requests.exceptions import HTTPError

from etcd.common_ops import CommonOps


class _LockBase(object):
    def __init__(self, client, lock_name, ttl):
        self.__client = client
        self.__lock_name = lock_name
        self.__path = '/' + lock_name
        self.__ttl = ttl

    def __enter__(self):
        self.acquire()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def acquire(self):
        raise NotImplementedError()

    def renew(self, ttl):
        raise NotImplementedError()

    def release(self):
        raise NotImplementedError()

    @property
    def client(self):
        return self.__client

    @property
    def lock_name(self):
        return self.__lock_name

    @property
    def path(self):
        return self.__path

    @property
    def ttl(self):
        return self.__ttl


class _Lock(_LockBase):
    """This lock will seek acquire an exclusive lock every time."""

    def __init__(self, client, lock_name, ttl):
        super(_Lock, self).__init__(client, lock_name, ttl)

        self.__index = None

    def acquire(self):
        self.client.debug("Acquiring lock: %s" % (self.path))

        parameters = { 'ttl': self.ttl }

        try:
          r = self.client.send(2, 
                               'post', 
                               self.path, 
                               module='lock', 
                               parameters=parameters,
                               return_raw=True)
        except HTTPError as e:
          if e.response.status_code == codes.internal_server_error:
            self.client.debug("There was a server-error while trying to "
                              "ACQUIRE an index lock. Make sure the key "
                              "hasn't been used for any other data: %s" % 
                              (self.path))

          raise
        else:
          self.__index = int(r.text)

    def renew(self, ttl):
        if self.__index is None:
          raise ValueError("Could not renew unacquired lock: %s" % (path))

        self.client.debug("Renewing lock: %s" % (self.path))

        parameters = { 'ttl': ttl }
        data = { 'index': self.__index }

        try:
          self.client.send(2, 
                           'put', 
                           self.path, 
                           module='lock', 
                           parameters=parameters,
                           data=data,
                           return_raw=True)
        except HTTPError as e:
          if e.response.status_code == codes.internal_server_error:
            self.client.debug("There was a server-error while trying to "
                              "RENEW an index lock. Make sure the key "
                              "has been acquired: %s" % (self.path))

          raise

    def get_active_index(self):
        parameters = { 'field': 'index' }

        try:
          r = self.client.send(2, 
                               'get', 
                               self.path, 
                               module='lock', 
                               parameters=parameters,
                               return_raw=True)
        except HTTPError as e:
          if e.response.status_code == codes.internal_server_error:
            self.client.debug("There was a server-error while trying to "
                              "get the active index of an index lock. Make "
                              "sure the key hasn't been used for any other "
                              "data: %s" % (self.path))

          raise
        else:
          return int(r.text) if r.text != '' else None

    def release(self):
        if self.__index is None:
          raise ValueError("Could not release unacquired lock: %s" % (path))

        self.client.debug("Releasing lock: %s" % (self.path))

        parameters = { 'index': self.__index }

        try:
          self.client.send(2, 
                           'delete', 
                           self.path, 
                           module='lock', 
                           parameters=parameters,
                           return_raw=True)
        except HTTPError as e:
          if e.response.status_code == codes.internal_server_error:
            self.client.debug("There was a server-error while trying to "
                              "release an index lock. Make sure the key "
                              "hasn't been used for any other data: %s" % 
                              (self.path))

          raise
        finally:
          self.__index = None


class _ReentrantLock(_LockBase):
    """This lock will allow the lock to be reacquired without blocking by 
    anything with the same instance-value.
    """

    def __init__(self, client, lock_name, instance_value, ttl):
        super(_ReentrantLock, self).__init__(client, lock_name, ttl)

        self.__instance_value = instance_value

    def acquire(self):
        self.client.debug("Acquiring rlock [%s]: %s" % 
                          (self.__instance_value, self.path))

        parameters = { 'ttl': self.ttl }

        try:
          self.client.send(2, 
                           'post', 
                           self.path, 
                           module='lock', 
                           parameters=parameters,
                           value=self.__instance_value,
                           return_raw=True)
        except HTTPError as e:
          if e.response.status_code == codes.internal_server_error:
            self.client.debug("There was a server-error while trying to "
                              "ACQUIRE a value lock [%s]. Make sure the key "
                              "hasn't been used for any other data: %s" % 
                              (self.__instance_value, self.path))

          raise

    def renew(self, ttl):
        self.client.debug("Renewing rlock [%s]: %s" % 
                          (self.__instance_value, self.path))

        parameters = { 'ttl': ttl }

        try:
          self.client.send(2, 
                           'put', 
                           self.path, 
                           module='lock', 
                           parameters=parameters,
                           value=self.__instance_value,
                           return_raw=True)
        except HTTPError as e:
          if e.response.status_code == codes.internal_server_error:
            self.client.debug("There was a server-error while trying to "
                              "RENEW a value lock [%s]. Make sure the key "
                              "has been acquired: %s" % 
                              (self.__instance_value, self.path))

          raise

    def get_active_value(self):
        try:
          r = self.client.send(2, 
                               'get', 
                               self.path, 
                               module='lock', 
                               return_raw=True)
        except HTTPError as e:
          if e.response.status_code == codes.internal_server_error:
            self.client.debug("There was a server-error while trying to "
                              "get the active value of a value lock [%s]. "
                              "Make sure the key hasn't been used for any "
                              "other data: %s" % 
                              (self.__instance_value, self.path))

          raise

        return r.text if r.text != '' else None

    def release(self):
        self.client.debug("Releasing rlock [%s]: %s" % 
                          (self.__instance_value, self.path))

        parameters = { 'value': self.__instance_value }

        try:
          self.client.send(2, 
                           'delete', 
                           self.path, 
                           module='lock', 
                           parameters=parameters,
                           return_raw=True)
        except HTTPError as e:
          if e.response.status_code == codes.internal_server_error:
            self.client.debug("There was a server-error while trying to "
                              "release a value lock [%s]. Make "
                              "sure the key hasn't been used for any other "
                              "data: %s" % (self.__instance_value, self.path))

          raise

        self.__instance_value = None


class LockMod(CommonOps):
    def __init__(self, client):
        self.__client = client

    def get_lock(self, lock_name, ttl):
        return _Lock(self.__client, lock_name, ttl)

    def get_rlock(self, lock_name, instance_value, ttl):
        return _ReentrantLock(self.__client, lock_name, instance_value, ttl)

# TODO: Is a lock deleted implicitly after expiration, or is it just somehow deactivated? I tried one key with the index lock, and I subsequently used the same key for a value lock, and I got a 500.
