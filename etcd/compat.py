try:
    from urlparse import parse_qsl, urlencode
except ImportError:
    from urllib.parse import parse_qsl, urlencode
