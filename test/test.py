from etcd.client import Client

c = Client()

print

r = c.node.set('/test_2056/val1', 5, ttl=60)
print(r)

print

r = c.node.set('/test_2056/val1', 5)
print(r)

from sys import exit
exit(0)

r = c.node.set('/test_2056/val2', 10)
print(r)

r = c.node.get('/test_2056/val1')
print(r.node.value)

r = c.node.get('/test_2056')
print(r)

#print("Collection:")
#for node in r.node.children:
#    print(node)

#r = c.node.delete('/test_2056/val1')
#print(r)

#r = c.node.delete('/test_2056/val2')
#print(r)

#r = c.directory.delete('/test_2056')
#print(r)

r = c.directory.delete_recursive('/test_2056')
print(r)
