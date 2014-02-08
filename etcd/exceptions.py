class EtcdException(Exception):
    """The base exception for the client."""

    pass

class EtcdError(EtcdException):
    """The base error for the client."""

    pass

class EtcdPreconditionException(EtcdException):
    """Raised when a CAS condition fails."""

    pass

class EtcdAlreadyExistsException(EtcdException):
    """Raised when a directory can't be created because it already exists."""

    pass

