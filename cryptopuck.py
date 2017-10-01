import os, getpass, pyinotify, time, argparse
import encrypt

class EventHandler(pyinotify.ProcessEvent):
    def __init__(self, public_key):
        self.public_key = public_key

    def process_IN_CREATE(self, event):
        if (os.path.isdir(event.pathname)):
            print ("New mounted volume detected: " + event.pathname)
            # Wait for the volume to be mounted and avoid permission errors
            time.sleep(1)
            encrypt.run(event.pathname, event.pathname, self.public_key)
            print("Finished volume encryption: " + event.pathname)


def main():
    parser_description = "Cryptopuck: Encrypt your drives on the fly"
    parser = argparse.ArgumentParser(description=parser_description)
    parser.add_argument("--public-key",
                        help="Path to the public key", required=True)
    args = parser.parse_args()

    mountpoint = os.path.join("/media", getpass.getuser())  # Linux only

    wm = pyinotify.WatchManager()  # Watch Manager
    mask = pyinotify.IN_CREATE  # watched events

    notifier = pyinotify.Notifier(wm, EventHandler(args.public_key))
    wdd = wm.add_watch(mountpoint, mask)

    notifier.loop()

if __name__ == "__main__":
    main()
