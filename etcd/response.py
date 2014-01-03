import pytz

from collections import namedtuple
from os.path import basename
from pytz import timezone
from datetime import datetime, timedelta

A_GET = 'get'
A_SET = 'set'
A_UPDATE = 'update'
A_CREATE = 'create'
A_DELETE = 'delete'
A_CAS = 'compareAndSwap'

def _build_node_object(action, node):
    if 'dir' not in node:
        node['dir'] = False

    if node['dir'] == True:
        if action == A_DELETE:
            return ResponseV2DeletedDirectoryNode(action, node)
# TODO: Specifically, what actions can happen for a DIRECTORY?
        else:
            return ResponseV2AliveDirectoryNode(action, node)
    else:
        if action == A_DELETE:
            return ResponseV2DeletedNode(action, node)
# TODO: Specifically, what actions can happen for a non-directory?
        else:
            return ResponseV2AliveNode(action, node)


class ResponseV2BasicNode(object):
    "Base-class representing all nodes: deleted, alive, or a collection."

    def __init__(self, action, node):
        self.action = action
        self.raw_node = node
        self.created_index = node['createdIndex']
        self.modified_index = node['modifiedIndex']
        self.key = node['key']

        # This is as involved as we'll get with whether nodes are hidden. Any 
        # more, and we'd have to manage and, therefore, translate every key 
        # reported by the server.
        self.is_hidden = basename(node['key']).startswith('_')

        # >> Process TTL-related stuff. 

        try:
            expiration = node['expiration']
        except KeyError:
            self.expiration = None
            self.ttl = None
            self.ttl_phrase = 'None'
        else:
            self.ttl = node['ttl']

            first_part = expiration[:19]
            naive_dt = datetime.strptime(first_part, '%Y-%m-%dT%H:%M:%S')
            tz_offset_hours = int(expiration[-5:-3])
            tz_offset_minutes = int(expiration[-2:])

            tz_offset = timedelta(seconds=(tz_offset_hours * 60 * 60 + 
                                           tz_offset_minutes * 60))

            self.expiration = (naive_dt + tz_offset).replace(tzinfo=pytz.UTC)
            self.ttl_phrase = ('%d: %s' % (self.ttl, self.expiration))

        # <<

        try:
            self.initialize(node)
        except NotImplementedError:
            pass

    def initialize(self, node):
        raise NotImplementedError()

    def __repr__(self):
        return ('<NODE(%s) [%s] [%s] IS_HID=[%s] IS_DEL=[%s] IS_DIR=[%s] '
                'IS_COLL=[%s] TTL=[%s] CI=(%d) MI=(%d)>' % 
                (self.__class__.__name__, self.action, self.key, 
                 self.is_hidden, self.is_deleted, self.is_directory, 
                 self.is_collection, self.ttl_phrase, self.created_index, 
                 self.modified_index))

    @property
    def is_deleted(self):
        return False

    @property
    def is_directory(self):
        return False

    @property
    def is_collection(self):
        return False


class ResponseV2AliveNode(ResponseV2BasicNode):
    "Base-class representing a single, non-deleted node."

    def initialize(self, node):
        self.value = node['value']


class ResponseV2DeletedNode(ResponseV2BasicNode):
    "Represents a single, deleted node."

    @property
    def is_deleted(self):
        return True


class ResponseV2DirectoryNode(ResponseV2BasicNode):
    """A base-class representing a single directory node, when children aren't 
    returned.
    """

    @property
    def is_directory(self):
        return True


class ResponseV2AliveDirectoryNode(ResponseV2DirectoryNode):
    """Represents a single DIRECTORY node either appearing in isolation or
    among siblings.
    """

    def initialize(self, node):
        if 'nodes' in node:
            self.__is_collection = True
            self.__raw_nodes = node['nodes']
        else:
            self.__is_collection = False
            self.__raw_nodes = None

    def __repr__(self):
        node_count_phrase = (len(self.__raw_nodes) \
                                if self.__raw_nodes is not None \
                                else '<NA>')

        return ('<NODE(%s) [%s] [%s] IS_HID=[%s] TTL=[%s] IS_DIR=[%s] '
                'IS_COLL=[%s] COUNT=[%s] CI=(%d) MI=(%d)>' % 
                (self.__class__.__name__, self.action, self.key, 
                 self.is_hidden, self.ttl_phrase, self.is_directory,
                 self.__is_collection, node_count_phrase, 
                 self.created_index, self.modified_index))

    @property
    def is_collection(self):
        return self.__is_collection

    @property
    def children(self):
        if self.__is_collection is False:
            raise ValueError("This directory node is not a collection.")

# TODO: This will need to cache the new objects for the benefit of repeated enumerations.
        for node in self.__raw_nodes:
            yield _build_node_object(self.action, node)


class ResponseV2DeletedDirectoryNode(ResponseV2DirectoryNode):
    """Represents a single DIRECTORY node either appearing in isolation or
    among siblings.
    """

    @property
    def is_deleted(self):
        return True


class ResponseV2(object):
    "An object that describes a response for every V2 request."

    def __init__(self, response, request_verb, request_path):
        response_raw = response.json()
        self.node = _build_node_object(response_raw['action'], 
                                       response_raw['node'])

    def __repr__(self):
        return ('<RESPONSE: %s>' % (self.node))
