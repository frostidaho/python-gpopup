#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import (namedtuple as _namedtuple,
                         OrderedDict as _OrderedDict,)

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib

from gpopup import utils as _utils
from gpopup.window_utils import Position, monitor_geometry
import gpopup.ipc as ipc
from gpopup.message_parsers import Parse

gtk = Gtk
gdk = Gdk

# https://developer.gnome.org/gtk3/stable/GtkListStore.html#gtk-list-store-new
class PyListStore(gtk.ListStore):
    def extend(self, rows):
        for row in rows:
            self.append(row)


class PyTreeView:
    def __init__(self, formatted_msg):
        headers = any(formatted_msg.columns)
        ls = self.get_liststore(formatted_msg)
        self.liststore = ls
        self.tree = gtk.TreeView.new_with_model(ls)
        self.tree.set_can_focus(False)
        self.tree.set_headers_clickable(False)
        sel = self.tree.get_selection()
        sel.set_mode(gtk.SelectionMode.NONE)

        for i, col in enumerate(formatted_msg.columns):
            nc = gtk.TreeViewColumn.new()
            nc.set_title(col)
            renderer = gtk.CellRendererText()
            nc.pack_start(renderer, expand=False)
            nc.set_attributes(renderer, text=i)
            self.tree.append_column(nc)
        self.show_headers = headers

    @staticmethod
    def get_liststore(msg):
        cols = msg.columns
        entries = [tuple(map(str, row)) for row in msg.entries]
        types = len(cols) * [str]
        mlist = PyListStore(*types)
        mlist.extend(entries)
        return mlist

    @property
    def show_headers(self):
        return self.tree.get_headers_visible()

    @show_headers.setter
    def show_headers(self, val):
        self.tree.set_headers_visible(val)

    @property
    def scrolledwindow(self):
        try:
            return self._scrolledwindow
        except AttributeError:
            sw = gtk.ScrolledWindow()
            sw.set_policy(
                # Relating to how to get a scrolledwindow to have the size of its contents
                # http://faq.pygtk.org/index.py?req=edit&file=faq10.028.htp
                hscrollbar_policy = gtk.PolicyType.NEVER,
                vscrollbar_policy = gtk.PolicyType.EXTERNAL,
            )
            sw.add(self.tree)
            self._scrolledwindow = sw
            return sw

class MainWindow(gtk.Window):
    nwins = 0
    _position = 'center'

    def __init__(self, formatted_msg):
        super().__init__()

        ptv = PyTreeView(formatted_msg)
        self.tree = ptv

        box = gtk.Box.new(gtk.Orientation.VERTICAL, 0)
        box.pack_start(ptv.scrolledwindow, True, True, 0)
        self.box = box
        
        self.set_name('gpopup')
        self.window_type = gtk.WindowType.TOPLEVEL
        # self.window_type = gtk.WindowType.POPUP
        # self.set_type_hint(gdk.WindowTypeHint.DIALOG)
        self.set_type_hint(gdk.WindowTypeHint.NOTIFICATION)

        # https://developer.gnome.org/icon-naming-spec/
        self.set_icon_name("dialog-information")
        self.add(box)
        
        self.__class__.nwins += 1
        self.connect("destroy", self.remove_window, None)
        self.connect("key-press-event", self.on_key_press)
        self.connect("button-release-event", self.on_button_release)
        # self.map_event_handler = self.connect('map-event', self.movewin)
        self.size_allocate_handler = self.connect('size-allocate', self.movewin)

        # keynames = ['Escape', 'n', 'p', 'Tab', 'Return']
        keynames = ['Escape']
        gdk_keys = {}
        for name in keynames:
            gdk_keys[name] = gdk.keyval_from_name(name)
        self.gdk_keys = gdk_keys

        # geom = gdk.Geometry()
        # geom.min_width = 1000
        # geom.max_width = 1200
        # geom.min_height = 500
        # geom.max_height = 900
        # geom.gravity = gdk.Gravity.EAST
        # geom.win_gravity 
        # gdk.WindowHints.WIN_GRAVITY
        # self.set_geometry_hints(
        #     None,
        #     geom,
        #     gdk.WindowHints.MAX_SIZE |
        #     gdk.WindowHints.MIN_SIZE |
        #     gdk.WindowHints.WIN_GRAVITY |
        #     gdk.WindowHints.USER_POS
        # )
        # self.position = 'nw'
        # self.set_default_size(100,100)
        # self.resize(100,100)
        mgeom = monitor_geometry()
        self.resize(mgeom.width // 8, mgeom.height // 6)
        self.show_all()
        
    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        if value in Position.__dict__:
            self._position = value
        else:
            raise ValueError('{} is not the name of a method in {}'.format(value, Position))

    def remove_window(self, widget, callback_data):
        """This is decrements a counter for how many windows are currently present
        kill gtk main loop only when the counter hits zero.
        """
        self.__class__.nwins -= 1
        if self.__class__.nwins <= 0:
            gtk.main_quit()
        
    def on_key_press(self, widget, event):
        key = event.keyval
        modifier = event.state

        gdk_keys = self.gdk_keys
        toret = None
        if key == gdk_keys['Escape']:
            self.destroy()

    def movewin(self, *pargs):
        gdkwin = self.get_window()
        try:
            geom = gdkwin.get_geometry()
            wsize = getattr(Position(*geom), self.position)
            gdkwin.move(wsize.x, wsize.y)
            if wsize == gdkwin.get_geometry():
                self.disconnect(self.size_allocate_handler)
        except AttributeError:
            pass

    # def on_button_press(self, widget, event):
    #     # For some reason you have to double click
    #     # for the button press event to be registered on the main window
    #     # for this reason we're just using the button-release-event
    #     self.destroy()
    def on_button_release(self, widget, event):
        self.destroy()

    def timeout_destroy(self, timeout=1.0):
        GLib.timeout_add_seconds(
            timeout,
            self.destroy,
        )


class NotifierServer(ipc.Server):
    position = 'center'
    def __init__(self, sock_name=ipc._DEFAULT_SOCK_NAME, force_bind=False):
        super().__init__(sock_name=sock_name, force_bind=force_bind)
        MainWindow.nwins += 1   # This is so that MainWindow doesn't kill the gtk.main loop
        self.notification_id = 0
        self.notifications = _OrderedDict()
        # self.position = position

    def cmd_new_window(self, formatted_msg, position=None):
        self.notification_id += 1
        n_id = self.notification_id
        win = MainWindow(formatted_msg)
        win.notification_id = n_id
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

    def cmd_new_from_markup(self, markup_string, position=None, parser='json'):
        formatted_msg = getattr(Parse, parser)(markup_string)
        return self.cmd_new_window(formatted_msg, position=position)

# class NotifierClient(ipc.BaseClient):
#     command_server = NotifierServer

NotifierClient = NotifierServer.get_client()
