from sys import exit

from etcd.client import Client

c = Client()

print

#print(c.server.get_version())
#print(c.server.get_leader_url_prefix())
#for machine in c.server.get_machines().node.children:
#    print(machine.value)
#
#print(c.server.get_dashboard_url())
#
#exit(0)

#l = c.module.lock.get_lock('test_lock_2')
#l.acquire(10)
#l.renew(150)
#l.release()
#
#exit(0)

#key = 'abc'
#value = 'some_value'
#c.module.leader.set_or_renew(key, value, 10)
#c.module.leader.get(key)
#c.module.leader.delete(key, value)
#
#exit(0)

# TODO: Is a lock deleted implicitly after expiration, or is it just somehow deactivated? I tried one key with the index lock, and I subsequently used the same key for a value lock, and I got a 500.

r = c.lock.get_rlock('test_lock_3', 'proc3')
#r.acquire(30)
r.release()
#
#r = c.lock.get_rlock('test_lock_3', 'proc3')
#r.acquire(60)
#r.release()
#
#r = c.lock.get_rlock('test_lock_3', 'proc4')
#r.acquire(30)
#r.release()

print("Active")
print(r.get_active_value())

exit(0)

#r = c.node.set('/test_2056/val1', 5, ttl=60)
#print(r)

#print

r = c.node.set('/test_2056/val1', 5, ttl=60)
print(r)

print

r = c.node.set('/test_2056/val2', 10)
print(r)

print

r = c.node.set('/test_2056/dir1/val11', 20)
print(r)

print

r = c.node.get('/test_2056/val1')
print(r)
#print(r.node.value)

print

#r = c.node.get('/test_2056', recursive=False)
#print(r)

r = c.node.get('/test_2056', recursive=True)
print(r)

for node in r.node.children:
    print("CHILD: %s" % (node))

exit(0)

#print("Collection:")
#for node in r.node.children:
#    print(node)

#r = c.node.delete('/test_2056/val1')
#print(r)

#r = c.node.delete('/test_2056/val2')
#print(r)

#r = c.directory.delete('/test_2056')
#print(r)

#print

#c.node.create_only('/test_2056/val3', 5)
#c.node.update_only('/test_2056/val1', 10)
#c.node.update_if_index('/test_2056/val1', 15, r.node.created_index)
#c.node.update_if_value('/test_2056/val1', 20, 5)

#r = c.node.compare_and_swap('/test_2056/val1', 30, current_value=5, prev_exists=True)
#print(r)

#r = c.node.get('/test_2056/val1')
#print(r.node.value)

r = c.directory.create('/test_2056/new_dir', ttl=60)
print(r)

print

r = c.directory.delete_recursive('/test_2056')
print(r)
