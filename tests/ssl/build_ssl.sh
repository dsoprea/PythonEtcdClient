#!/bin/sh

# Create server certs.
openssl genrsa -out etcd.local.key 2048
openssl req -new -key etcd.local.key -out etcd.local.csr

# Sign server certs.
openssl x509 -req -in etcd.local.csr -CA rootCA.pem -CAkey rootCA.key -CAcreateserial -out etcd.local.crt -days 500
