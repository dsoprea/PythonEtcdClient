from sys import exit

from etcd.client import Client

c = Client()

print

print("Waiting:")
r = c.node.wait('/test_2056/val1')

print(r)
