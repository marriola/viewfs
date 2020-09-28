import sdnotify

class SystemNotifier:
    def __init__(self):
        self.systemd = sdnotify.SystemdNotifier()

    def ready(self):
        self.systemd.notify('READY=1')

    def stopping(self):
        self.systemd.notify('STOPPING=1')
