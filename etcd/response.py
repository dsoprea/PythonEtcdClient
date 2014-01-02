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
        if action == A_GET:
            return ResponseV2DirectoryCollection(action, node)
        elif action == A_SET:
            return ResponseV2AliveDirectoryNode(action, node)
        elif action == A_DELETE:
            return ResponseV2DeletedDirectoryNode(action, node)
# TODO: What other types of actions can happen for a DIRECTORY?
        else:
            raise ValueError("Unrecognized directory response 'action': %s" % (action))
    else:
        if action == A_DELETE:
            return ResponseV2DeletedNode(action, node)
# TODO: What other types of actions can happen for a non-directory node?
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
        self.is_hidden = basename(node['key']).startswith('_')

        try:
            self.initialize(node)
        except NotImplementedError:
            pass

    def initialize(self, node):
        raise NotImplementedError()

    def __repr__(self):
        return ('<NODE(%s) [%s] [%s] IS_HID=[%s] IS_DEL=[%s] IS_DIR=[%s] '
                'IS_COLL=[%s] CI=(%d) MI=(%d)>' % 
                (self.__class__.__name__, self.action, self.key, 
                 self.is_hidden, self.is_deleted, self.is_directory, 
                 self.is_collection, self.created_index, self.modified_index))

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

    def __repr__(self):
        if self.ttl is None:
            ttl_phrase = 'None'
        else:
            ttl_phrase = ('%d: %s' % (self.ttl, self.expiration))

        return ('<NODE(%s) [%s] [%s] IS_HID=[%s] IS_DEL=[%s] IS_DIR=[%s] '
                'IS_COLL=[%s] CI=(%d) MI=(%d) TTL=[%s]>' % 
                (self.__class__.__name__, self.action, self.key, 
                 self.is_hidden, self.is_deleted, self.is_directory, 
                 self.is_collection, self.created_index, self.modified_index, 
                 ttl_phrase))

    def initialize(self, node):
        try:
            expiration = node['expiration']
        except KeyError:
            self.expiration = None
        else:
            first_part = expiration[:19]
            naive_dt = datetime.strptime(first_part, '%Y-%m-%dT%H:%M:%S')
            tz_offset_hours = int(expiration[-5:-3])
            tz_offset_minutes = int(expiration[-2:])

            tz_offset = timedelta(seconds=(tz_offset_hours * 60 * 60 + 
                                           tz_offset_minutes * 60))

            self.expiration = (naive_dt + tz_offset).replace(tzinfo=pytz.UTC)
        try:
            self.ttl = node['ttl']
        except KeyError:
            self.ttl = None

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


class ResponseV2DeletedDirectoryNode(ResponseV2DirectoryNode):
    """Represents a single DIRECTORY node either appearing in isolation or
    among siblings.
    """

    @property
    def is_deleted(self):
        return True


class ResponseV2DirectoryCollection(ResponseV2AliveDirectoryNode):
    "Represents the list of nodes when a directory is returned."

    def initialize(self, node):
        self.__raw_nodes = node['nodes']

    def __repr__(self):
        return ('<NODE(%s) [%s] [%s] IS_HID=[%s] COUNT=(%d) CI=(%d) MI=(%d)>' % 
                (self.__class__.__name__, self.action, self.key, 
                 self.is_hidden, len(self.__raw_nodes), self.created_index, 
                 self.modified_index))

    @property
    def is_directory(self):
        return True

    @property
    def is_collection(self):
        return True

    @property
    def children(self):
# TODO: This will need to cache the new objects for the benefit of repeated enumerations.
        for node in self.__raw_nodes:
            yield _build_node_object(self.action, node)


class ResponseV2(object):
    "An object that describes a response for every V2 request."

    def __init__(self, response, request_verb, request_path):
        response_raw = response.json()
        self.node = _build_node_object(response_raw['action'], 
                                       response_raw['node'])

    def __repr__(self):
        return ('<RESPONSE: %s>' % (self.node))

# TODO: We need to handle the "TTL" expired response. Does this happen on a GET?
