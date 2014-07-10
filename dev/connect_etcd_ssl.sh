#!/bin/sh

curl --cacert ssl/ca.crt.pem --key ssl/client.key.pem --cert ssl/client.crt.pem https://server.etcd:4001/v2/keys/_etcd/machines -w "%{http_code}" -k && echo
