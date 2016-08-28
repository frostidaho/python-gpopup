#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import namedtuple as _namedtuple

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk

from gpopup import utils as _utils

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
        for i, col in enumerate(formatted_msg.columns):
            nc = gtk.TreeViewColumn.new()
            nc.set_title(col)
            renderer = gtk.CellRendererText()
            # nc.pack_start(renderer, False)
            nc.pack_start(renderer, expand=False)
            nc.set_attributes(renderer, text=i)
            # cols.append(nc)
            self.tree.append_column(nc)
        self.show_headers = headers

    @staticmethod
    def get_liststore(msg):
        # msg = format_msg(message, columns)
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
    def __init__(self, formatted_msg):
        ptv = PyTreeView(formatted_msg)
        self.tree = ptv

        box = gtk.Box.new(gtk.Orientation.VERTICAL, 0)
        box.pack_start(ptv.scrolledwindow, True, True, 0)
        self.box = box

        super().__init__()
        self.set_name('gpopup')
        self.window_type = gtk.WindowType.TOPLEVEL
        self.set_type_hint(gdk.WindowTypeHint.DIALOG)
        self.set_icon_name("dialog-question")
        self.add(box)
        # self.set_hexpand(True)
        self.show_all()
        self.__class__.nwins += 1
        self.connect("destroy", self.remove_window, None)
        self.connect("key-press-event", self.on_key_press)

        # keynames = ['Escape', 'n', 'p', 'Tab', 'Return']
        keynames = ['Escape']
        gdk_keys = {}
        for name in keynames:
            gdk_keys[name] = gdk.keyval_from_name(name)
        self.gdk_keys = gdk_keys

    def remove_window(self, widget, callback_data):
        """This is decrements a counter for how many windows are currently present
        kill gtk main loop only when the counter hits zero.
        """
        self.__class__.nwins -= 1
        if self.__class__.nwins <= 0:
            gtk.main_quit()
        
    def on_key_press(self, widget, event):
        key = event.keyval
        # keyname = gdk.keyval_name(key)
        modifier = event.state

        gdk_keys = self.gdk_keys
        toret = None
        if key == gdk_keys['Escape']:
            self.destroy()

def get_window(formatted_msg):
    w = MainWindow(formatted_msg)
    return w

