import requests

from etcd.common_ops import CommonOps


class _LockBase(object):
    def __init__(self, client, lock_name, ttl):
        self.__client = client
        self.__lock_name = lock_name
        self.__ttl = ttl
        self.__path = '/' + lock_name

    def __enter__(self):
        self.acquire()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def acquire(self):
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
    def ttl(self):
        return self.__ttl

    @property
    def path(self):
        return self.__path


class _Lock(_LockBase):
    """This lock will seek acquire an exclusive lock every time."""

    def __init__(self, client, lock_name, ttl):
        super(_Lock, self).__init__(client, lock_name, ttl)

        self.__index = None

    def acquire(self):
        parameters = { 'ttl': self.ttl }
        r = self.client.send(2, 
                             'post', 
                             self.path, 
                             module='lock', 
                             parameters=parameters,
                             return_raw=True)

        self.__index = int(r.text())

    def renew(self, ttl):
        parameters = { 'ttl': ttl }
        data = { 'index': self.__index }
# TODO: What does this return?
        self.client.send(2, 
                         'put', 
                         self.path, 
                         module='lock', 
                         parameters=parameters,
                         data=data,
                         return_raw=True)

    def get_active_index(self):
        parameters = { 'field': 'index' }
        r = self.client.send(2, 
                             'get', 
                             self.path, 
                             module='lock', 
                             parameters=parameters,
                             return_raw=True)

        return int(r.text())

    def release(self):
        parameters = { 'index': self.__index }
# TODO: What does this return?
        r = self.__client.send(2, 
                               'delete', 
                               self.__path, 
                               module='lock', 
                               parameters=parameters,
                               return_raw=True)


class _ReentrantLock(_LockBase):
    """This lock will allow the lock to be reacquired without blocking by 
    anything with the same instance-value.
    """

    def __init__(self, client, lock_name, ttl, instance_value):
        super(_Lock, self).__init__(client, lock_name, ttl)

        self.__instance_value = instance_value

    def acquire(self):
        parameters = { 'ttl': self.ttl }
        self.client.send(2, 
                           'post', 
                           self.path, 
                           module='lock', 
                           parameters=parameters,
                           value=self.__instance_value,
                           return_raw=True)

    def renew(self, ttl):
        parameters = { 'ttl': ttl }
# TODO: What does this return?
        self.client.send(2, 
                           'put', 
                           f.path, 
                           module='lock', 
                           parameters=parameters,
                           value=self.__instance_value,
                           return_raw=True)

    def get_active_value(self):
        r = self.__client.send(2, 
                               'get', 
                               self.path, 
                               module='lock', 
                               return_raw=True)

        return r.text()

    def release(self):
        parameters = { 'value': self.__instance_value }
# TODO: What does this return?
        self.__client.send(2, 
                           'delete', 
                           self.__path, 
                           module='lock', 
                           parameters=parameters,
                           return_raw=True)


class LockOps(CommonOps):
    def __init__(self, client):
        self.__client = client

    def get_lock(self, lock_name, ttl):
        return _Lock(self.__client, lock_name, ttl)

    def get_reentrant_lock(self, lock_name, ttl, instance_value):
        return _ReentrantLock(self.__client, lock_name, ttl, instance_value)
