@!/bin/sh

# Create CA.
openssl genrsa -out rootCA.key 2048
openssl req -x509 -new -nodes -key rootCA.key -days 1024 -out rootCA.pem

