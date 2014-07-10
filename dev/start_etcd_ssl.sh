#!/bin/sh

etcd -f -ca-file=ssl/ca.crt.pem -cert-file=ssl/server.crt.pem -key-file=ssl/server.key.pem -data-dir=data -addr=server.etcd:4001 -peer-addr=server.etcd:7001 -name machine0
