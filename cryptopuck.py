import os, getpass, asyncore, pyinotify, time
import encrypt

class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        if (os.path.isdir(event.pathname)):
            print ("Creating:" + event.pathname)
            time.sleep(1)  # Wait for the volume to be fully mounted
            encrypt.run(event.pathname, event.pathname, "./key.public")
            print("Done with encryption of " + event.pathname)


def main():
    mountpoint = os.path.join("/media", getpass.getuser())  # Linux only

    wm = pyinotify.WatchManager()  # Watch Manager
    mask = pyinotify.IN_CREATE  # watched events

    notifier = pyinotify.AsyncNotifier(wm, EventHandler())
    wdd = wm.add_watch(mountpoint, mask)

    asyncore.loop()

if __name__ == "__main__":
    main()
