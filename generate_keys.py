from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

# #Quick way to generate a new key
# private_key = RSA.generate(2048)
#
# #Show the real content of the private part to console, be careful with this!
# print(private_key.exportKey())
#
# #Get the public part
# public_key = private_key.publickey()
#
# #Show the real content of the public part to console
# print(public_key.exportKey())
#
# #Save both keys into some file for future usage if needed
# with open("rsa.pub", "wb") as pub_file:
#     pub_file.write(public_key.exportKey())
#
# with open("rsa.pvt", "wb") as pvt_file:
#     pvt_file.write(private_key.exportKey())
#
# #Load public key back from file and we only need public key for encryption
# with open('rsa.pub', 'r') as pub_file:
#     pub_key = RSA.importKey(pub_file.read())
#
# #Encrypt something with public key and print to console
# cipher = PKCS1_OAEP.new(pub_key)
# encrypted = cipher.encrypt("Hello world".encode("UTF-8"))
#
# #Load private key back from file and we must need private key for decryption
# with open('rsa.pvt', 'r') as pvt_file:
#     pvt_key = RSA.importKey(pvt_file.read())
#
# #Decrypt the text back with private key and print to console
# cipher = PKCS1_OAEP.new(pvt_key)
# decrypted = cipher.decrypt(encrypted)
# print(decrypted.decode("UTF-8"))



def main():
    # Generate private key
    private_key = RSA.generate(2048)
    # Derive the public key
    public_key = private_key.publickey()
    # Save the keys into files
    with open("key.public", "wb") as public_file:
        public_file.write(public_key.exportKey())
    with open("key.private", "wb") as private_file:
        private_file.write(private_key.exportKey())

if __name__ == "__main__":
    main()
