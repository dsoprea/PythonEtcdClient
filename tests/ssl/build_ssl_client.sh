#!/bin/sh

# Create server certs.
openssl genrsa -out client.key 2048
openssl req -new -key client.key -out client.csr

# Sign server certs.
openssl x509 -extensions ssl_client -req -in client.csr -CA rootCA.pem -CAkey rootCA.key -CAcreateserial -out client.crt -days 500
