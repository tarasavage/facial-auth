# Token Service

This package provides functionality for generating and validating tokens using RSA encryption.

## Generating RSA Keys

### Using OpenSSL (Command Line)

1. Generate a private key:

   ```bash
   openssl genrsa -out private_key.pem 2048
   ```
2. Extract the public key from the private key:

   ```bash
   openssl rsa -in private_key.pem -pubout -out public_key.pem
   ```
