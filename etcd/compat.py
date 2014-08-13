try:
    from urlparse import parse_qsl
    from urllib import urlencode
except ImportError:
    from urllib.parse import parse_qsl, urlencode
