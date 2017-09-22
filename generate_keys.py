"""
Script to generate a private and public RSA key.

The public key should be deployed on the Cryptopuck and will be used to encrypt
the AES secret which will have encrypted the files.
"""

import argparse
from Crypto.PublicKey import RSA


def main():
    parser_description = "Generate a public and private RSA key pair"
    parser = argparse.ArgumentParser(description=parser_description)
    parser.add_argument("--destination",
                        help="Path to where the key pair will be exported",
                        default="./")
    args = parser.parse_args()

    # Generate private key
    private_key = RSA.generate(2048)
    # Derive the public key
    public_key = private_key.publickey()
    # Save the keys into files
    public_key_file = args.destination + "key.public"
    private_key_file = args.destination + "key.private"
    with open(public_key_file, "wb") as public_file:
        public_file.write(public_key.exportKey())
    with open(private_key_file, "wb") as private_file:
        private_file.write(private_key.exportKey())

if __name__ == "__main__":
    main()
