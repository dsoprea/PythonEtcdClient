import requests

from requests.status_codes import codes
from requests.exceptions import HTTPError

from etcd.common_ops import CommonOps


class _LockBase(object):
    def __init__(self, client, lock_name):
        self.__client = client
        self.__lock_name = lock_name
        self.__path = '/' + lock_name

    def __enter__(self):
        self.acquire()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def acquire(self, ttl):
        raise NotImplementedError()

    def renew(self, ttl):
        raise NotImplementedError()

    def get_active_value(self):
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


class _Lock(_LockBase):
    """This lock will seek acquire an exclusive lock every time."""

    def __init__(self, client, lock_name):
        super(_Lock, self).__init__(client, lock_name)

        self.__index = None

    def acquire(self, ttl_s):
        self.client.debug("Acquiring lock: %s" % (self.path))

        parameters = { 'ttl': ttl_s }

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

    def renew(self, ttl_s):
        if self.__index is None:
          raise ValueError("Could not renew unacquired lock: %s" % (path))

        self.client.debug("Renewing lock: %s" % (self.path))

        parameters = { 'ttl': ttl_s }
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
          return int(r.text)

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

    def __init__(self, client, lock_name, instance_value):
        super(_ReentrantLock, self).__init__(client, lock_name)

        self.__instance_value = instance_value

    def acquire(self, ttl_s):
        self.client.debug("Acquiring rlock [%s]: %s" % 
                          (self.__instance_value, self.path))

        parameters = { 'ttl': ttl_s }

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

    def renew(self, ttl_s):
        self.client.debug("Renewing rlock [%s]: %s" % 
                          (self.__instance_value, self.path))

        parameters = { 'ttl': ttl_s }

        try:
          self.client.send(2, 
                           'put', 
                           f.path, 
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

        return r.text

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


class LockOps(CommonOps):
    def __init__(self, client):
        self.__client = client

    def get_lock(self, lock_name):
        return _Lock(self.__client, lock_name)

    def get_rlock(self, lock_name, instance_value):
        return _ReentrantLock(self.__client, lock_name, instance_value)
