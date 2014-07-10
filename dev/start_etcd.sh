#!/bin/sh

etcd -f -data-dir=data -addr=server.etcd:4001 -peer-addr=server.etcd:7001 -name machine0
