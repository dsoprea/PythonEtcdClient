class EtcdException(Exception):
    """The base exception for the client."""

    pass

#class EtcdHttpException(EtcdException):
#    def __init__(self, message, response):
#        super(EtcdHttpException, self).__init__(message)
#        self.__code = response.status_code
#
#    @property
#    def code(self):
#        return self.__code
#
#class EtcdHttpNotFoundException(EtcdHttpException):
#    pass

class EtcdPreconditionException(EtcdException):
    """Raised when a CAS condition fails."""

    pass
