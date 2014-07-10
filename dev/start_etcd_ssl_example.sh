#!/bin/sh

etcd -f -name machine0 -data-dir machine0 -ca-file=ssl/ca.crt.pem -cert-file=ssl/server.crt.pem -key-file=ssl/server.key.pem
