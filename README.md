Introduction
------------

*PEC* was created as a more elegant and proper client for *etcd* than existing 
solutions. It has an intuitive construction, provides access to the 
complete *etcd* API (of 0.2.0+), and just works.

Every request returns a standard and obvious result, and HTTP exceptions are 
re-raised as Python-standard exceptions where it makes sense (like "KeyError").

The full API is documented [here](http://python-etcd-client.readthedocs.org/en/latest/).


Quick Start
-----------

There's almost nothing to it:

```python
from etcd import Client

# Uses the default *etcd* port on *localhost* unless told differently.
c = Client()

c.node.set('/test/key', 5)

r = c.node.get('/test/key')

print(r.node.value)
# Displays "5".
```

General Functions
-----------------

These functions represent the basic key-value functionality of *etcd*.

Set a value:

```python
# Can provide a "ttl" parameter with seconds, for expiration.
r = c.node.set('/node_test/subkey1', 5)

print(r)
# Prints: <RESPONSE: <NODE(ResponseV2AliveNode) [set] [/node_test/subkey1] 
#           IS_HID=[False] IS_DEL=[False] IS_DIR=[False] IS_COLL=[False] 
#           TTL=[None] CI=(5) MI=(5)>>
```

Get a value:

```python
r = c.node.get('/node_test/subkey1')

print(r)
# Prints: <RESPONSE: <NODE(ResponseV2AliveNode) [get] [/node_test/subkey1] 
#           IS_HID=[False] IS_DEL=[False] IS_DIR=[False] IS_COLL=[False] 
#           TTL=[None] CI=(5) MI=(5)>>

print(r.node.value)
# Prints "5"
```

Get children:

```python
r = c.node.set('/node_test/subkey2', 10)

print(r)
# Prints: <RESPONSE: <NODE(ResponseV2AliveNode) [set] [/node_test/subkey2] 
#           IS_HID=[False] IS_DEL=[False] IS_DIR=[False] IS_COLL=[False] 
#           TTL=[None] CI=(6) MI=(6)>>

r = c.node.get('/node_test')

print(r)
# Prints: <RESPONSE: <NODE(ResponseV2AliveDirectoryNode) [get] [/node_test] 
#           IS_HID=[False] TTL=[None] IS_DIR=[True] IS_COLL=[True] 
#           COUNT=[2] CI=(5) MI=(5)>>
```

Get children, recursively:

```python
r = c.node.get('/node_test', recursive=True)

print(r)
# Prints: <RESPONSE: <NODE(ResponseV2AliveDirectoryNode) [get] [/node_test] 
#           IS_HID=[False] TTL=[None] IS_DIR=[True] IS_COLL=[True] 
#           COUNT=[2] CI=(5) MI=(5)>>

for node in r.node.children:
    print(node)

# Prints:
# <NODE(ResponseV2AliveNode) [get] [/node_test/subkey1] IS_HID=[False] 
#   IS_DEL=[False] IS_DIR=[False] IS_COLL=[False] TTL=[None] CI=(5) MI=(5)>
# <NODE(ResponseV2AliveNode) [get] [/node_test/subkey2] IS_HID=[False] 
#   IS_DEL=[False] IS_DIR=[False] IS_COLL=[False] TTL=[None] CI=(6) MI=(6)>
```

Delete node:

```python
r = c.node.delete('/node_test/subkey2')

print(r)
# Prints: <RESPONSE: <NODE(ResponseV2DeletedNode) [delete] 
#           [/node_test/subkey2] IS_HID=[False] IS_DEL=[True] 
#           IS_DIR=[False] IS_COLL=[False] TTL=[None] CI=(6) MI=(7)>>
```


Compare and Swap Functions
--------------------------

These functions represent *etcd*'s atomic comparisons. These allow for a "set"-
type operation when one or more conditions are met.

The core call takes one or more of the following conditions as arguments:

    current_value
    prev_exists
    current_index

If none of the conditions are given, the call acts like a *set()*. If a condition
is given that fails, a *etcd.exceptions.EtcdPreconditionException* is raised.

The core call is:

```python
r = c.node.compare_and_swap('/cas_test/val1', 30, current_value=5, 
                            prev_exists=True, current_index=5)
```

The following convenience functions are also provided, but only allow you to 
check one, specific condition:

```python
r = c.node.create_only('/cas_test/val1', 5)

print(r)
# Prints: <RESPONSE: <NODE(ResponseV2AliveNode) [create] [/cas_test/val1] 
#           IS_HID=[False] IS_DEL=[False] IS_DIR=[False] IS_COLL=[False] 
#           TTL=[None] CI=(10) MI=(10)>>

r = c.node.update_only('/cas_test/val1', 10)

print(r)
# Prints: <RESPONSE: <NODE(ResponseV2AliveNode) [update] [/cas_test/val1] 
#           IS_HID=[False] IS_DEL=[False] IS_DIR=[False] IS_COLL=[False] 
#           TTL=[None] CI=(10) MI=(13)>>

r = c.node.update_if_index('/cas_test/val1', 15, r.node.modified_index)

print(r)
# Prints: <RESPONSE: <NODE(ResponseV2AliveNode) [compareAndSwap] 
#           [/cas_test/val1] IS_HID=[False] IS_DEL=[False] IS_DIR=[False] 
#           IS_COLL=[False] TTL=[None] CI=(10) MI=(14)>>

r = c.node.update_if_value('/cas_test/val1', 20, 15)

print(r)
# Prints: <RESPONSE: <NODE(ResponseV2AliveNode) [compareAndSwap] 
#           [/cas_test/val1] IS_HID=[False] IS_DEL=[False] IS_DIR=[False] 
#           IS_COLL=[False] TTL=[None] CI=(10) MI=(15)>>
```


Directory Functions
-------------------

These functions represent directory-specific calls. Whereas creating a node has 
side-effects that contribute to directory management (like creating a node 
under a directory implicitly creates the directory), these functions are 
directory specific.

Create directory:

```python
# Can provide a "ttl" parameter with seconds, for expiration.
r = c.directory.create('/dir_test/new_dir')

print(r)
# Prints: <RESPONSE: <NODE(ResponseV2AliveDirectoryNode) [set] 
#           [/dir_test/new_dir] IS_HID=[False] TTL=[None] IS_DIR=[True] 
#           IS_COLL=[False] COUNT=[<NA>] CI=(16) MI=(16)>
```

Remove an empty directory:

```python
r = c.directory.delete('/dir_test/new_dir')

print(r)
# Prints: <RESPONSE: <NODE(ResponseV2DeletedDirectoryNode) [delete] 
#           [/dir_test/new_dir] IS_HID=[False] IS_DEL=[True] IS_DIR=[True] 
#           IS_COLL=[False] TTL=[None] CI=(16) MI=(17)>>
```

Recursively remove a directory, and any contents:

```python
c.directory.create('/dir_test/new_dir')
c.directory.create('/dir_test/new_dir/new_subdir')

# This will raise a requests.exceptions.HTTPError ("403 Client Error: 
# Forbidden") because it has children.
r = c.directory.delete('/dir_test/new_dir')

# You have to recursively delete it.
r = c.directory.delete_recursive('/dir_test')

print(r)
# Prints: <RESPONSE: <NODE(ResponseV2DeletedDirectoryNode) [delete] 
#           [/dir_test] IS_HID=[False] IS_DEL=[True] IS_DIR=[True] 
#           IS_COLL=[False] TTL=[None] CI=(16) MI=(20)>>
```


Server Functions
----------------

These functions represent calls that return information about the server or 
cluster.

Get version of the specific host being connected to:

```python
r = c.server.get_version()

print(r)
# Prints "0.2.0-45-g98351b9", on my system.
```

The URL prefix of the current cluster leader:

```python
r = c.server.get_leader_url_prefix()

print(r)
# Prints "http://127.0.0.1:7001" with my single-host configuration.
```

Enumerate the prefixes of the hosts in the cluster:

```python
machines = c.server.get_machines()

print(machines)
# Prints: [(u'etcd', u'http://127.0.0.1:4001'), 
           (u'raft', u'http://127.0.0.1:7001')]
```

Get URL of the dashboard for the server being connected-to:

```python
r = c.server.get_dashboard_url()

print(r)
# Prints: http://127.0.0.1:4001/mod/dashboard
```


In-Order-Keys Functions
-----------------------

These calls represent the in-order functionality, where a directory can be used 
to store a series of values with automatically-assigned, increasing keys. 
Though not quite sufficient as a queue, this might be used to automatically 
generate unique keys for a set of values.

Enqueue values:

```python
io = c.inorder.get_inorder('/queue_test')

io.add('value1')
io.add('value2')
```

Enumerate existing values:

```python
# If you want to specifically return the entries in order of the keys 
# (which is to say that they're in insert-order), use the "sorted"
# parameter.
r = io.list()

for child in r.node.children:
    print(child.value)

# Prints:
# value1
# value2
```


Locking Module Functions
------------------------

These functions represent the fair locking functionality that comes packaged.

### Standard Locking

A simple, distributed lock:

```python
l = c.module.lock.get_lock('test_lock_1', ttl=10)
l.acquire()
l.renew(ttl=30)
l.release()
```

This returns the index of the current lock holder:

```python
l.get_active_index()
```

It's also available as a *with* statement:

```python
with c.module.lock.get_lock('test_lock_1', ttl=10):
    print("In lock 1.")
```

### Reentrant Locking

Here, a name for the lock is provided, as well as a value that represents a 
certain locking purpose, process, or host. Subsequent requests having the same 
value currently stored for the lock will return immediately, where others will 
block until the current lock has been released or expired. 

This can be used when certain parts of the logic need to participate during the 
same lock, or a specific function/etc might be invoked multiple times during a 
lock.

This is the basic usage (nearly identical to the traditional lock):

```python
rl = c.module.lock.get_rlock('test_lock_2', 'proc1', ttl=10)
rl.acquire()
rl.renew(ttl=30)
rl.release()
```

This returns the current value of the lock holder(s):

```python
rl.get_active_value()
```

This is also provided as a *with* statement:

```python
with c.module.lock.get_rlock('test_lock_2', 'proc1', ttl=10):
    print("In lock 2.")
```


Leader Election Module Functions
--------------------------------

The leader-election API does consensus-based assignment, meaning that, of all 
of the clients potentially attempting to assign a value to a name, only one 
assignment will be allowed for a certain period of time, or until the key is
deleted.

To set or renew a value:

```python
c.module.leader.set_or_renew('consensus-based key', 'test value', ttl=10)
```

To get the current value:

```python
# This will return:
# > A non-empty string if the key is set and unexpired.
# > None, if the key was set but has been expired or deleted.
r = c.module.leader.get('consensus-based key')

print(r)
# Prints "test value".
```

To delete the value (will fail unless there's an unexpired value):

```python
c.module.leader.delete('consensus-based key', 'test value')
```
