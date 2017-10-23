# Cryptopuck
Pocket sized encryption for your removable media!

![cryptopuck photo](https://i.imgur.com/oeMtpH1.jpg)

## What
Cryptopuck is a hand-held device that will encrypt whatever drive gets attached to it. Currently, the encryption is performed on a Raspberry Pi Zero, but the software should work on any Linux system that can run Python. The device enables its users to encrypt their removable media on the fly, simply by plugging them in Cryptopuck.

The concept is based on the Cryptopuck **not** being able to decrypt the files and the user being in the position to feasibly claim incapable of decrypting the files. This is because the private key that can decrypt the files cannot be memorized and is remotely stored. Therefore it cannot be compromised by the perpetrator who might get hold of the Cryptopuck device that encrypted the files. However, since this is a filesystem level encryption the Cryptopuck user cannot deny that they have encrypted the files. Additionally, the file sizes are visible but not other kind of metadata such as the filenames, which are safely encrypted.

The software is made up of the following Python 3 scripts:
  * `cryptopuck.py`
    * Contains the main business logic, i.e. detects when a drive is mounted and encrypts it. Will only work on Linux.
  * `encrypt.py`
    * Encrypts the given source folder and outputs the encrypted files in the given destination folder. If the source and destination folders are the same then the initial unencrypted files are removed after they are encrypted. Will work on both Windows and Linux.
  * `decrypt.py`
    * Decrypts the given source folder and outputs the decrypted files in the given destination folder. If the source and destination folders are the same then the initial encrypted files are removed after they are encrypted. Will work on both Windows and Linux.
  * `generate_keys.py`
    * Generates a 2048-bit RSA public and private key pair. You should deploy the public key and safely store the private one remotely. Will work on both Windows and Linux.

**DISCLAIMER:** Please keep in mind this is a **proof-of-concept** system that toys around with the idea of a portable gadget that will encrypt your removable media. It incorporates hardware and software which have neither been audited nor designed for security-critical applications. There is absolutely no guarantee that your files will be safely encrypted or remain in tact after using Cryptopuck.

## How
The Cryptopuck software is written in Python 3 and is automatically launched after each boot. It detects when a new removable medium is mounted and encrypts it. The files are encrypted symmetrically, with AES-256 using a randomly generated 32-byte key. This key is then placed among the encrypted files, but not before it is itself encrypted with an RSA asymmetric algorithm. The files are given random names and are all placed in the root directory in order for the file structure to be hidden. The original structure is saved in a JSON file  that gets encrypted and is also placed among the other files.

The encrypted medium can be decrypted using the private key. Specifically, the private key decrypts the symmetric key which then in turn decrypts the rest of the files and the file structure is restored.

## Why
There are many reasons you would want to encrypt your removable media on the fly. Maybe you are a reporter who has gotten hold of important files or a photographer in a warzone and need to cross some checkpoints. Perhaps you need to deliver your proprietary corporate software to a customer or an off-site location and cannot have it being transported around in clear form. Or you just want to encrypt your drive before passing the nosy TSA check at the airport. Or wait, that could get you into more trouble so don't do it! :laughing:

## How to set up
To set things up, you will need to get your RPi Zero connected to the Internet and some very light soldering to put everything together will be necessary. Neither of these topics will be covered here.

### Software
  * Get the latest Raspbian image. The one I used was **2017-09-07-raspbian-stretch-lite**.
  * Connect via SSH (or otherwise) to your RPi.
  * `sudo apt-get update --fix-missing`
  * Install `pip` for Python 3:
    * `sudo apt-get install python3-pip`
  * Install the Python 3 dependencies. Expect this to take way more time than it does on your own computer:
    * `pip3 install pycrypto`
    * `pip3 install pyinotify`
    * `pip3 install RPi.GPIO`
  * Install `udiskie` which will help us automount the removable drives:
    * `sudo apt-get install python3-udiskie`
  * `udiskie` will not allow you to mount disks as a non-root user. That is technically not necessary, but I did not like it, so I made some changes in the configuration files.
    * `sudo nano /usr/share/polkit-1/actions/org.freedesktop.udisks2.policy`
    * Change all `<allow_any>auth_admin</allow_any><allow_inactive>auth_admin</allow_inactive>` to:
    * `<allow_any>yes</allow_any><allow_inactive>yes</allow_inactive>`
  * Use RPi's hardware random number generator to generate entropy.
    * Install `rng-tools`:
      * sudo apt-get install rng-tools
    * Enable the use of `/dev/hwrng` by editing `/etc/default/rng-tools`:
      * sudo nano /etc/default/rng-tools
      * Add `HRNGDEVICE=/dev/hwrng` to the file (or uncomment the existing entry)
  * Launch the script on start-up as non-root user by adding it before `exit 0` in `/etc/rc.local`:
    * `sudo nano /etc/rc.local`
    * Add the following lines:
```bash
# Run udiskie
su pi -c '/usr/bin/udiskie --no-notify --no-file-manager &'

# Create mountpoint if it does not exist so we can monitor it with the Python script
su pi -c '/bin/mkdir -p /media/pi'

# Run Cryptopuck and save logs
su pi -c '/usr/bin/python3 /home/pi/cryptopuck/cryptopuck.py --mountpoint=/media/pi/ --public-key=/home/pi/cryptopuck/key.public >> /home/pi/cryptopuck.log 2>&1 &'
```
  * Transfer this repository to RPi's `/home/pi` folder. You can either use `git` or copy the files directly to the microSD card.
  * Generate the public and private key pair:
    * `python3 generate_keys.py`
  * Move the private key (`key.private`) off the Cryptopuck. **You should never use Cryptopuck with the private key stored on the Raspberry Pi as if the perpetrator discovers it, they will be able to decrypt your files.**
  * If you wish to never have stored the private key on the Cryptopuck, do the above process on your own computer and transfer **the public key** to the Cryptopuck.
  * That was about it! After you have encrypted the drive, you can plug it into your computer where the private key is stored to decrypt your files. To achieve that, you should install the Python 3 and PyCrypto on your computer and use the `decrypt.py` script:
    * `python3 decrypt.py --source=/path/to/your/drive/ --destination=/path/to/your/drive/ --private-key=/path/to/your/key.private`

### Hardware
  * [Cryptopuck 3D printed case](https://tinkercad.com/things/dcRE6oUcA1A)
  * Raspberry Pi Zero
  * DC Step-up module (3.3V to 5V)
  * Micro-USB OTG cable
  * 1400mAh Li-Po battery
  * On/Off switch
  * 5mm LED
  * 220Ω resistor

## Media
  * Watch a demo and read the story behind Cryptopuck at [platis.solutions](https://platis.solutions/blog/2017/10/10/cryptopuck-encrypt-removable-media-on-the-fly/)

## FAQ
  * **Q:** Why don't you encrypt the whole volume which would be safer and would not expose any metadata like the file sizes?
    * **A:** There are two main reasons behind this design choice. To begin with, encrypting the whole drive would be slow and so are USB 2.0 connection as well as the Raspberry Pi Zero. Encrypting the whole drive with the current hardware setup would dramatically increase the time needed to encrypt the drive. Moreover, the encrypted volume (e.g. LUKS) would not be read without additional software on other platforms such as Windows. Cryptopuck should be simple and fast to use.
  * **Q:** Why don't you ZIP the files before encrypting them so to protect some of their metadata?
    * **A:** Same answer as above. The current hardware setup is too slow to perform this operation in a satisfactory manner time-wise.
  * **Q:** Are you aware that just removing the clear-text files is not enough as recoverable traces could remain?
    * **A:** Yes, that is absolutely accurate but this is an acceptable trade-off at the moment. Overwriting the non-used space with random data will, on one hand, dramatically slow the whole procedure down. On the other, it does not completely guarantee everything will be overwritten due to the wear-leveling features of modern USB devices.
  * **Q:** Why do you encrypt the files with AES and then the AES key with RSA instead of RSA directly?
    * **A:** Encrypting arbitrarily large files with RSA is not the commonly suggested approach as it would be too slow. Encrypting symmetrically and then encrypting the symmetric key with a public key, provides similar levels of security at higher efficiency. This, of course, assuming the symmetric key is sufficiently random.
  * **Q:** What happens if someone confiscates my Cryptopuck? Are my files still secure?
    * **A:** Yes, your files should still be as secure as they were, provided you never stored your private key inside the Cryptopuck. However, the Cryptopuck could have been compromised! **Do not use it again without ensuring its software and hardware integrity first.**
  * **Q:** Should I depend my `[life/freedom/industrial secrets/X]` on this?
    * **A:** If you value them, **do not**. This is a proof-of-concept system, using cheap and general-purpose materials, that has not been audited.
