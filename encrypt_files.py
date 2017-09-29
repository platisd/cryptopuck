import sys, os, struct, argparse
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

def encrypt_file(key, in_filename, out_dir="", chunksize=64*1024):
    """ Encrypts a file using AES (CBC mode) with the
        given key.

        Adopted from Eli Bendersky's example:
        http://eli.thegreenplace.net/2010/06/25/aes-encryption-of-files-in-python-with-pycrypto/

        Arguments:
            key             The encryption key - a string that must be
                            either 16, 24 or 32 bytes long. Longer keys
                            are more secure.
            in_filename     Path to the file to be encrypted.
            out_dir         Path to the folder where the encrypted file will be
                            generated. The encrypted file name will be the
                            original plus the `.enc` suffix.
            chunksize       Sets the size of the chunk which the function
                            uses to read and encrypt the file. Larger chunk
                            sizes can be faster for some files and machines.
                            chunksize must be divisible by 16.
    """
    out_filename = os.path.basename(in_filename) + '.enc'

    iv = os.urandom(16)
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    filesize = os.path.getsize(in_filename)

    with open(in_filename, 'rb') as infile:
        with open(out_dir + out_filename, 'wb') as outfile:
            outfile.write(struct.pack('<Q', filesize))
            outfile.write(iv)

            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += ' '.encode("UTF-8") * (16 - len(chunk) % 16)

                outfile.write(encryptor.encrypt(chunk))


def encrypt_aes_secret(aes_secret, public_key_file):
    """ Encrypt the AES secret using our public key.

        Arguments:
            aes_secret          The AES secret in plain text to encrypt
            public_key_file     The public key to be used for encryption

        Return:
            encrypted_aes_secret   The encrypted AES key using the public key
    """

    with open(public_key_file, 'r') as pub_file:
        pub_key = RSA.importKey(pub_file.read())

    cipher = PKCS1_OAEP.new(pub_key)
    encrypted_aes_secret = cipher.encrypt(aes_secret)
    return encrypted_aes_secret


def main():
    parser_description = "Encrypt a directory"
    parser = argparse.ArgumentParser(description=parser_description)
    parser.add_argument("--source",
                        help="Path to the directory with the files to encrypt",
                        required=True)
    destination_message = "Path to the directory where the encrypted files \
will be exported. If none provided, the same as the source will be selected \
and the original files will be removed."
    parser.add_argument("--destination", help=destination_message)
    parser.add_argument("--public-key",
                        help="Path to the public key", default="./key.public")
    args = parser.parse_args()

    # Check to see if there is actually a public key file
    if not os.path.isfile(args.public_key):
        print ("Public key not found: " + args.public_key)
        sys.exit(1)

    # If no destination was provided, then the destination is the source
    if not args.destination:
        args.destination = args.source

    # Generate a random AES secret that will encrypt the files
    aes_secret = os.urandom(32)

    # Recursively encrypt all files in the source folder
    for dirpath, dirnames, filenames in os.walk(args.source):
        for name in filenames:
            filename = os.path.join(dirpath, name)
            encrypt_file(aes_secret, filename, args.destination)
            # If we are encrypting in the same folder as the clear text files
            # then remove the original unencrypted files
            if args.source == args.destination:
                if os.path.exists(filename):
                    os.remove(filename)

    # Encrypt and save our AES secret using the public key for the holder of
    # the private key to be able to decrypt the files.
    with open(args.destination + "aes_secret", "wb") as key_file:
        key_file.write(encrypt_aes_secret(aes_secret, args.public_key))


if __name__ == "__main__":
    main()
