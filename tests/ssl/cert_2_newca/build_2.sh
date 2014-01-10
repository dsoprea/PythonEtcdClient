openssl genrsa -des3 -passout pass:x -out alien_client.pass.key 2048
openssl rsa -passin pass:x -in alien_client.pass.key -out alien_client.key
rm alien_client.pass.key 
openssl req -new -key alien_client.key -out alien_client.csr
openssl x509 -req -days 365 -in alien_client.csr -signkey alien_client.key -out alien_client.crt

