import os, struct
import argparse
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


def decrypt_file(key, in_filename, out_filename=None, chunksize=24*1024):
    """ Decrypts a file using AES (CBC mode) with the
        given key. Parameters are similar to encrypt_file,
        with one difference: out_filename, if not supplied
        will be in_filename without its last extension
        (i.e. if in_filename is 'aaa.zip.enc' then
        out_filename will be 'aaa.zip')
    """
    if not out_filename:
        out_filename = os.path.splitext(in_filename)[0]

    with open(in_filename, 'rb') as infile:
        origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
        iv = infile.read(16)
        decryptor = AES.new(key, AES.MODE_CBC, iv)

        with open(out_filename, 'wb') as outfile:
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
    with open(private_key_file, 'r') as pvt_file:
        pvt_key = RSA.importKey(pvt_file.read())

    cipher = PKCS1_OAEP.new(pvt_key)
    decrypted_aes_secret = cipher.decrypt(encrypted)
    return decrypted_aes_secret


def main():
    parser_description = "Decrypt a directory containing encrypted files"
    parser = argparse.ArgumentParser(description=parser_description)
    parser.add_argument("--source",
                        help="Path to the directory with the encrypted files",
                        default=".")
    parser.add_argument("--destination",
                        help="Path to the directory where the unencrypted files will be exported",
                        default=".")
    parser.add_argument("--secret",
                        help="Path to the (encrypted) AES secret file")
    args = parser.parse_args()


    if not args.secret:
        args.secret = args.source + "/key.private"

if __name__ == "__main__":
    main()
