from sys import exit

from etcd.client import Client

c = Client()

print

#r = c.node.set('/test_2056/val1', 5, ttl=60)
#print(r)

#print

r = c.node.set('/test_2056/val1', 5)
print(r)

print

r = c.node.set('/test_2056/val2', 10)
print(r)

print

r = c.node.get('/test_2056/val1')
print(r.node.value)

print

#r = c.node.get('/test_2056')
#print(r)

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
c.node.update_if_value('/test_2056/val1', 20, 5)

r = c.node.get('/test_2056/val1')
print(r.node.value)

r = c.directory.delete_recursive('/test_2056')
print(r)
