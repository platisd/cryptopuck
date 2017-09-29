import sys, os, struct, argparse
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


def decrypt_file(key, in_filename, out_dir="", out_filename=None, chunksize=24*1024):
    """ Decrypts a file using AES (CBC mode) with the given key.

        Adopted from Eli Bendersky's example:
        http://eli.thegreenplace.net/2010/06/25/aes-encryption-of-files-in-python-with-pycrypto/

    Arguments:
        key             AES secret to decrypt the file.
        in_filename     Path to the decrypted file.
        out_dir         Path to the output folder of the decrypted file.
        out_filename    The name of the decrypted file. If no name is supplied
                        the decrypted file name will be the original one minus
                        the last ending (e.g. example.txt.enc -> example.txt).
        chunksize       Size of the chunks to read while decrypting.
    """
    if not out_filename:
        out_filename = os.path.basename(os.path.splitext(in_filename)[0])

    with open(in_filename, 'rb') as infile:
        origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
        iv = infile.read(16)
        decryptor = AES.new(key, AES.MODE_CBC, iv)

        with open(out_dir + out_filename, 'wb') as outfile:
            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                outfile.write(decryptor.decrypt(chunk))

            outfile.truncate(origsize)


def decrypt_aes_secret(aes_secret, private_key_file):
    """ Decrypt the AES key so we can use it to decrypt the other files

    Arguments:
        aes_secret              The encrypted AES secret
        private_key_file        The private key to decrypt the AES secret

    Return:
        decrypted_aes_secret    The decrypted AES secret
    """
    with open(private_key_file, "r") as pvt_file:
        pvt_key = RSA.importKey(pvt_file.read())

    with open(aes_secret, "rb") as aes_secret_file:
        secret = aes_secret_file.read()

    cipher = PKCS1_OAEP.new(pvt_key)
    decrypted_aes_secret = cipher.decrypt(secret)
    return decrypted_aes_secret


def main():
    parser_description = "Decrypt a directory containing encrypted files"
    parser = argparse.ArgumentParser(description=parser_description)
    parser.add_argument("--source",
                        help="Path to the directory with the encrypted files",
                        required=True)
    destination_message = "Path to the directory where the unencrypted files \
will be exported"
    parser.add_argument("--destination", help=destination_message,
                        required=True)
    secret_help_message = "Path to the (encrypted) AES secret file. If none \
provided, a file named `aes_secret` from the source folder will be used."
    parser.add_argument("--secret", help=secret_help_message)
    parser.add_argument("--private-key", help="Path to the private key",
                        default="./key.private")
    args = parser.parse_args()

    # Decrypt the AES secret
    # Set default path if None provided
    if not args.secret:
        args.secret = args.source + "aes_secret"
    # Check to see if there is actually an AES secret file
    if not os.path.isfile(args.secret):
        print ("AES secret not found: " + args.secret)
        sys.exit(1)
    # Check to see if there is actually a private key file
    if not os.path.isfile(args.private_key):
        print ("Private key not found: " + args.private_key)
        sys.exit(1)
    # Get the decrypted AES key
    decrypted_aes_secret = decrypt_aes_secret(args.secret, args.private_key)

    # Recursively unencrypt all files in the source folder except the secret
    for dirpath, dirnames, filenames in os.walk(args.source):
        for name in filenames:
            filename = os.path.join(dirpath, name)
            if filename != args.secret:
                decrypt_file(decrypted_aes_secret, filename, args.destination)

if __name__ == "__main__":
    main()
