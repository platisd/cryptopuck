"""
Script to decrypt the files.

Decrypts the given source folder and outputs the decrypted files in the given
destination folder. If the source and destination folders are the same then the
initial encrypted files are removed after they are encrypted. Will work on
both Windows and Linux.
"""

import sys
import os
import struct
import argparse
import json
import tempfile
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


def decrypt_file(key, in_filename, out_filename=None, chunksize=24*1024):
    """ Decrypts a file using AES (CBC mode) with the given key.

        Adopted from Eli Bendersky's example:
        http://eli.thegreenplace.net/2010/06/25/aes-encryption-of-files-in-python-with-pycrypto/

    Arguments:
        key             AES secret to decrypt the file.
        in_filename     Path to the decrypted file.
        out_filename    The name (and path) of the decrypted file. If no name
                        is supplied the decrypted file name will be the
                        original one minus the last ending
                        (e.g. example.txt.enc -> example.txt).
        chunksize       Size of the chunks to read while decrypting.
    """
    if not out_filename:
        out_filename = os.path.basename(os.path.splitext(in_filename)[0])

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


def decrypt_string(text_to_decrypt, private_key_file):
    """ Decrypt the supplied string using our private key.

    Arguments:
        text_to_decrypt         The encrypted text
        private_key_file        The private key to decrypt

    Return:
        decrypted_text          The decrypted text
    """
    with open(private_key_file, "r") as pvt_file:
        pvt_key = RSA.importKey(pvt_file.read())

    cipher = PKCS1_OAEP.new(pvt_key)
    decrypted_text = cipher.decrypt(text_to_decrypt)
    return decrypted_text


def run(source, destination, secret, private_key="./key.private"):
    """ Decrypts the source folder and outputs to the destination folder.

        Arguments:
            source          The folder to be decrypted
            destination     The folder where the decrypted files will end up
            secret          The (encrypted) secret used for the encryption
            public_key      The private key to be used for the decryption
    """
    # Make sure that the source and destination folders finish with separator
    if source[-1] != os.sep:
        source += os.sep
    if destination[-1] != os.sep:
        destination += os.sep

    # Decrypt the AES secret
    # Set default path if None provided
    if not secret:
        secret = source + "secret"
    # Check to see if there is actually an AES secret file
    if not os.path.isfile(secret):
        print("Secret not found: " + secret)
        sys.exit(1)
    # Check to see if there is actually a private key file
    if not os.path.isfile(private_key):
        print("Private key not found: " + private_key)
        sys.exit(1)
    # Get the decrypted AES key
    with open(secret, "rb") as aes_secret_file:
        aes_secret = aes_secret_file.read()
    decrypted_aes_secret = decrypt_string(aes_secret, private_key)

    # We should restore the file structure, therefore we should parse the file
    # containing the encrypted structure and create the appropriate filepaths.
    # To do that we need to restore the mapping that contains the
    # real to obscured paths combinations. The keys are the obscured filenames
    # and the values are the real paths.
    json_encrypted_map = source + "filenames_map"
    # Dictionary to hold the mapping between encrypted and real paths
    filenames_map = dict()
    if not os.path.isfile(json_encrypted_map):
        print("Warning: Will not restore file structure.")
        warning_msg = "Map between encrypted filenames and paths not found: "
        print(warning_msg + json_encrypted_map)
    else:
        # Unencrypt the json containing the filenames map into a temporary file
        with tempfile.NamedTemporaryFile(mode="r+t") as tmp_json:
            decrypt_file(decrypted_aes_secret, json_encrypted_map,
                         tmp_json.name)
            tmp_json.seek(0)  # Go to the beginning of the file to read again
            filenames_map = json.load(tmp_json)

    # Recursively unencrypt files in the source folder
    for dirpath, dirnames, filenames in os.walk(source):
        for name in filenames:
            filename = os.path.join(dirpath, name)
            # Do not unencrypt files that we have generated ourselves
            if filename != secret and filename != json_encrypted_map:
                # If the filenames mapping is defined, then we should use it
                # to restore the original file structure
                if filenames_map:
                    # Get the real filename and its path
                    destination_file = destination + filenames_map[name]
                    # Create the necessary folder structure
                    folder_structure = os.path.dirname(destination_file)
                    os.makedirs(folder_structure, exist_ok=True)
                else:
                    # If for some reason the filenames map is not defined then
                    # suffix the files to indicate that they are decrypted
                    destination_file = destination + name + ".clear"
                print("Decrypting: " + filename)
                decrypt_file(decrypted_aes_secret, filename, destination_file)
            # If we are decrypting in the same folder as the encrypted files
            # then remove the original encrypted files
            if source == destination:
                if os.path.exists(filename):
                    os.remove(filename)


def main():
    parser_description = "Decrypt a directory containing encrypted files"
    parser = argparse.ArgumentParser(description=parser_description)
    parser.add_argument("--source",
                        help="Path to the directory with the encrypted files",
                        required=True)
    destination_message = "Path to the directory where the unencrypted files \
    will be exported. If it is the same as the source folder, then the \
    existing encrypted files will be removed."
    parser.add_argument("--destination", help=destination_message,
                        required=True)
    secret_help_message = "Path to the (encrypted) AES secret file. If none \
    provided, a file named `secret` from the source folder will be used."
    parser.add_argument("--secret", help=secret_help_message)
    parser.add_argument("--private-key", help="Path to the private key",
                        default="./key.private")
    args = parser.parse_args()

    run(args.source, args.destination, args.secret, args.private_key)

if __name__ == "__main__":
    main()
