import requests
import requests.status_codes


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


class EtcdEmptyResponseError(EtcdError):
    pass


class EtcdWaitFaultException(EtcdException):
    pass


class EtcdAtomicWriteError(EtcdError):
    pass


def translate_exceptions(method):
   def op_wrapper(self, path, *args, **kwargs):
        try:
            return method(self, path, *args, **kwargs)
        except requests.HTTPError as e:
            # We're only concerned with generating KeyError's when appropriate.

            if e.response.status_code == \
                    requests.status_codes.codes.precondition_failed:
                r = EtcdPreconditionException()
            elif e.response.status_code == \
                    requests.status_codes.codes.not_found:
                try:
                    j = e.response.json()
                except ValueError:
                    raise

                if j['errorCode'] != 100:
                    raise

                r = KeyError(path)
            else:
                raise

        raise r

   return op_wrapper
