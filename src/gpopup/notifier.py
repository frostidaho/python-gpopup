import gpopup.ipc as ipc
from gpopup.message_widgets import MainWindow
from collections import OrderedDict as _OrderedDict


class NotifierServer(ipc.Server):
    position = 'center'
    def __init__(self, sock_name=ipc._DEFAULT_SOCK_NAME, force_bind=False):
        super().__init__(sock_name=sock_name, force_bind=force_bind)
        MainWindow.nwins += 1   # This is so that MainWindow doesn't kill the gtk.main loop
        self.notifications = _OrderedDict()

    def cmd_new_window(self, *messages, position=None):
        win = MainWindow(*messages)
        n_id = win.win_id
        self.notification_id = n_id
        win.connect("destroy", self._remove_notif_id, n_id)
        if position is None:
            win.position = self.position
        else:
            win.position = position
        self.notifications[n_id] = win
        # return win
        return n_id

    def cmd_hide(self, notification_id=None):
        if notification_id is None:
            notification_id = self.notification_id
        win = self.notifications[notification_id]
        win.hide()

    def cmd_show(self, notification_id=None):
        if notification_id is None:
            notification_id = self.notification_id
        win = self.notifications[notification_id]
        win.show()
        win.movewin()           # Move to old position after showing
        # This call to movewin appears necessary in QTile


    def _remove_notif_id(self, gtk_mainwindow=None, n_id=None):
        del self.notifications[n_id]
        try:
            self.notification_id = list(self.notifications)[-1]
        except IndexError:
            # FIXME this should probably be something like MainWindow.win_id
            self.notification_id = 0

    def cmd_destroy(self, notification_id=None):
        if notification_id is None:
            notification_id = self.notification_id
        win = self.notifications[notification_id]
        win.destroy()
        # The call to _remove_notif_id is taken care by connecting
        # a callback to the destroy event on the MainWindow widget itself
        # self._remove_notif_id(notification_id)

    def cmd_timeout(self, timeout=1.0, notification_id=None):
        if notification_id is None:
            notification_id = self.notification_id
        win = self.notifications[notification_id]
        win.timeout_destroy(timeout)

    def cmd_movewin(self, position=None, notification_id=None):
        if notification_id is None:
            notification_id = self.notification_id
        win = self.notifications[notification_id]
        if position is not None:
            win.position = position
        win.movewin()
        return win.position


class NotifierClient(ipc.BaseClient):
    "Client associated with NotifierServer"
    command_server = NotifierServer
    sock_name = NotifierServer.sock_name

