#!/bin/sh

sphinx-apidoc -F -H "Python etcd Client" -A "Dustin Oprea" -V $1 -d 2 -o docs etcd 

