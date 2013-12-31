from collections import namedtuple
from os.path import basename

A_GET = 'get'
A_SET = 'set'
A_CREATE = 'create'
A_DELETE = 'delete'
A_CAS = 'compareAndSwap'

def _build_node_object(action, node):
    if 'dir' not in node:
        node['dir'] = 'false'

    if node['dir'] == 'true':
        if self.action == A_GET:
            return ResponseV2NodeCollection(self.action, node)
        elif self.action in A_SET:
            return ResponseV2DirectoryAliveNode(self.action, node)
        elif self.action in A_DELETE:
            return ResponseV2DirectoryDeletedNode(self.action, node)
    else:
        if self.action == A_DELETE:
            return ResponseV2DeletedNode(self.action, node)
        else:
            return ResponseV2FullNode(self.action, node)


class ResponseV2BasicNode(object):
    "Base-class representing all nodes: deleted, alive, or a collection."

    def __init__(self, action, node):
        self.action = action
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

    @property
    def is_deleted(self):
        return False

    @property
    def is_directory(self):
        return False

    @property
    def is_collection(self):
        return False


class ResponseV2AliveNode(object):
    "Base-class representing a single, non-deleted node."

    def __init__(self, action, node):
        try:
            self.expiration = node['expiration']
        except KeyError:
            self.expiration = None

        try:
            self.ttl = node['ttl']
        except KeyError:
            self.ttl = None

        super(ResponseV2Node, self).__init__(action, node)


class ResponseV2DeletedNode(ResponseV2BasicNode):
    "Represents a single, deleted node."

    @property
    def is_deleted(self):
        return True


class ResponseV2FullNode(ResponseV2AliveNode):
    """Represents a single FILE node either appearing in isolation or among 
    siblings.
    """

    def initialize(self, node):
        self.value = node['value']


class ResponseV2DirectoryNode(ResponseV2BasicNode):
    """A base-class representing a single directory node, when children aren't 
    returned.
    """

    @property
    def is_directory(self):
        return True


class ResponseV2DirectoryAliveNode(ResponseV2DirectoryNode):
    """Represents a single DIRECTORY node either appearing in isolation or
    among siblings.
    """


class ResponseV2DirectoryDeletedNode(ResponseV2DirectoryNode):
    """Represents a single DIRECTORY node either appearing in isolation or
    among siblings.
    """

    @property
    def is_deleted(self):
        return True


class ResponseV2NodeCollection(ResponseV2AliveNode):
    "Represents the list of nodes when a directory is returned."

    def initialize(self, node):
        self.__raw_nodes = node['nodes']

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
            yield _build_node_object(node)


class ResponseV2(object):
    "An object that describes a response for every V2 request."

    def __init__(self, response, request_verb, request_path):
        response_raw = response.json()
        node_raw = response_raw['node']
        self.node = _build_node_object(node_raw)

# TODO: We need to handle the "TTL" expired response. Does this happen on a GET?
