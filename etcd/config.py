from os import environ

DEFAULT_HOSTNAME = environ.get('PEC_HOSTNAME', '127.0.0.1')
"Default hostname for server."

DEFAULT_PORT = int(environ.get('PEC_PORT', '4001'))
"Default port for server."

DEFAULT_SCHEME = environ.get('PEC_SCHEME', 'http')
"Default scheme for server."

HOST_FAIL_WAIT_S = 5
"Number of seconds that must elapse before we're allowed to retry a host."
