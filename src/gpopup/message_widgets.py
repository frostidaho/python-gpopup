import logging as _logging
_log = _logging.getLogger(__name__)
_log.addHandler(_logging.NullHandler())

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
# Set font of a CellRendererText using Pango
# http://faq.pygtk.org/index.py?req=show&file=faq13.040.htp
gi.require_version('Pango', '1.0')
from gi.repository import Pango

from gpopup.window_utils import Position, monitor_geometry
from collections import namedtuple as _namedtuple
from itertools import repeat as _repeat
from itertools import zip_longest as _zip_longest

class PyListStore(Gtk.ListStore):
    def extend(self, rows):
        for row in rows:
            self.append(row)


class BaseWidget:
    def __init__(self, message):
        """
        A base class for message widgets.

        Subclasses of BaseWidget should take an instance of a
        message class (from message_types) and create corresponding
        graphical widgets.

        The top-most widget for each message is given by the attribute
        basewidget.primary
        """
        self.message = message
        wopts = self.message.widget_opts
        # _option_setter needs to be called before and after initializing the widgets
        #  because some of the options require the underlying widget to work with
        self._option_setter(wopts)
        self._init_widget()
        self._option_setter(wopts)
        _log.debug('Widget options are: {}'.format(self.message.widget_opts))

    def _option_setter(self, opts):
        for k,v in opts.items():
            try:
                setattr(self, k, v)
            except AttributeError:
                _log.debug("Can't set {} to {} right now".format(k, v))

    @property
    def primary(self):
        return self._primary

    def _init_widget(self):
        raise NotImplementedError

    @property
    def monitor_geometry(self):
        try:
            return self._monitor_geometry
        except AttributeError:
            self._monitor_geometry = monitor_geometry()
            return self._monitor_geometry


class TableWidget(BaseWidget):
    min_rows = 2
    max_rows = 11
    max_col_width_frac = 0.33
    # columns_font = ''

    def _init_widget(self):
        ls = self.get_liststore(self.message)
        self.liststore = ls
        self.tree = Gtk.TreeView.new_with_model(ls)
        self.tree.set_can_focus(False)
        self.tree.set_headers_clickable(False)
        self.tree.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
        sel = self.tree.get_selection()
        sel.set_mode(Gtk.SelectionMode.NONE)

        max_col_width = int(self.max_col_width_frac * self.monitor_geometry.width)
        col_n_font = zip(self.message.columns, self.columns_font, self.columns_alignment)
        for i, cnf in enumerate(col_n_font):
            col, font, align = cnf
            tv_col = self._make_treeview_col(idx=i, colname=col, max_col_width=max_col_width, font=font, alignment=align)
            self.tree.append_column(tv_col)
        self.show_headers = any(self.message.columns)

    @staticmethod
    def _make_treeview_col(idx=0, colname='', max_col_width=500, font='', alignment=0.5):
        nc = Gtk.TreeViewColumn.new()
        nc.set_title(colname)
        renderer = Gtk.CellRendererText()
        if font:
            font_descr = Pango.font_description_from_string(font)
            renderer.set_property('font-desc', font_descr)
        nc.set_alignment(0.5)
        # nc.set_resizable(True)
        renderer.set_alignment(alignment, 0.5)
        # https://developer.gnome.org/gtk3/stable/GtkTreeViewColumn.html#gtk-tree-view-column-set-expand
        nc.set_expand(True)
        nc.pack_start(renderer, expand=True)
        nc.set_attributes(renderer, text=idx)
        nc.set_max_width(int(max_col_width))
        return nc

    @staticmethod
    def get_liststore(msg):
        cols = msg.columns
        entries = [tuple(map(str, row)) for row in msg.body]
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
    def columns_alignment(self):
        try:
            ca = self._columns_alignment
        except AttributeError:
            return _repeat(0.5)
        d = {
            'LEFT': 0.0,
            'CENTER': 0.5,
            'RIGHT': 1.0,
        }
        if isinstance(ca, str):
            return _repeat(d[ca])
        else:
            return [d[x] for x in ca]

    @columns_alignment.setter
    def columns_alignment(self, val):
        aligns = set(('LEFT', 'RIGHT', 'CENTER'))
        def test_str(val_str):
            if val_str not in aligns:
                raise ValueError('Alignment {!r} is not one of {!r}'.format(val, aligns))
        if isinstance(val, str):
            val = val.upper()
            test_str(val)
            self._columns_alignment = val
        else:
            vals = [x.upper() for x in val]
            for val_str in vals:
                test_str(val_str)
            self._columns_alignment = vals

    @property
    def columns_font(self):
        try:
            cf = self._columns_font
        except AttributeError:
            return _repeat('')
        if isinstance(cf, str):
            return _repeat(cf)
        else:
            return cf

    @columns_font.setter
    def columns_font(self, val):
        self._columns_font = val

    @property
    def primary(self):
        try:
            return self._scrolledwindow
        except AttributeError:
            sw = Gtk.ScrolledWindow()
            sw.set_policy(
                # Relating to how to get a scrolledwindow to have the size of its contents
                # http://faq.pyGtk.org/index.py?req=edit&file=faq10.028.htp
                hscrollbar_policy = Gtk.PolicyType.NEVER,
                # vscrollbar_policy = Gtk.PolicyType.EXTERNAL,
                vscrollbar_policy = Gtk.PolicyType.AUTOMATIC,
            )
            sw.add(self.tree)
            self._scrolledwindow = sw
            nrows = len(self.liststore) +2 # +2 due to headers
            min_rows = self.min_rows # +2 due to headers
            max_rows = self.max_rows + 2 # +2 due to headers

            nrows = min([max_rows, nrows])
            nrows = max([min_rows, nrows])
            _log.debug('Number of rows to display is: {}'.format(nrows))
            sw.set_min_content_height(nrows * self.get_row_height())
            return sw

    def get_row_height(self):
        cols = self.tree.get_columns()
        height = [x.cell_get_size() for x in cols]
        height = max([x.height for x in height])
        spacing = max([x.get_spacing() for x in cols])
        _log.debug('Max row height = {}, Row spacing = {}'.format(height, spacing))
        return height + spacing

class SimpleWidget(BaseWidget):
    def _init_widget(self):
        box =  Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        # https://developer.gnome.org/gtk3/stable/GtkBox.html#gtk-box-pack-start
        if self.message.summary:
            summary = '<b>{}</b>'.format(self.message.summary)
            self.summary = self.new_label(summary)
            box.pack_start(self.summary, False, True, 0)

        if self.message.body:
            self.body = self.new_label(self.message.body)
            box.pack_start(self.body, False, True, 0)
        self._primary = box

    @staticmethod
    def new_label(text, use_markup=True):
        label = Gtk.Label.new(text)
        label.set_use_markup(use_markup)
        return label

_DestroyInfo = _namedtuple('_DestroyInfo', 'id timeout')
class MainWindow(Gtk.Window):
    nwins = 0
    win_id = 0
    _position = 'center'

    def __init__(self, *messages):
        super().__init__()
        self._scheduled_destroyers = set()
        self._new_destroyers = set()

        box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        lb = Gtk.ListBox()
        lb.set_selection_mode(Gtk.SelectionMode.NONE)
        box.pack_start(lb, True, True, 0)

        for msg in messages:
            row = Gtk.ListBoxRow()
            row.add(msg.get_widget().primary)
            lb.add(row)
        self.add(box)
        
        self.set_name('gpopup')
        self.window_type = Gtk.WindowType.TOPLEVEL # Maybe try WindowType.POPUP
        self.set_type_hint(Gdk.WindowTypeHint.NOTIFICATION) # Maybe try WindowTypeHint.DIALOG

        # https://developer.gnome.org/icon-naming-spec/
        self.set_icon_name("dialog-information")
        
        self.__class__.nwins += 1
        self.win_id = self.next_win_id()
        self.connect("destroy", self.remove_window, None)
        self.connect("key-press-event", self.on_key_press)
        self.connect("button-release-event", self.on_button_release)
        self.connect("focus-in-event", self.rm_timeout_destroy)
        self.connect("focus-out-event", self.add_timeout_destroy)
        

        keynames = ['Escape']
        gdk_keys = {}
        for name in keynames:
            gdk_keys[name] = Gdk.keyval_from_name(name)
        self.gdk_keys = gdk_keys

        mgeom = self.monitor_geometry
        self.resize(mgeom.width // 8, mgeom.height // 8)
        self.show_all()
        self.size_allocate_handler = self.connect('size-allocate', self.movewin)
        
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
            Gtk.main_quit()
        
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

    def on_button_release(self, widget, event):
        self.destroy()

    def add_timeout_destroy(self, widget, event):
        for timeout in self._new_destroyers:
            self.timeout_destroy(timeout)
        self._new_destroyers.clear()

    def rm_timeout_destroy(self, widget, event):
        _log.debug('Unscheduling widget.destroy: {}'.format(self._scheduled_destroyers))
        for timeout_destr in list(self._scheduled_destroyers):
            GLib.source_remove(timeout_destr.id)
            self._scheduled_destroyers.discard(timeout_destr)
            self._new_destroyers.add(timeout_destr.timeout)

    def timeout_destroy(self, timeout=1.0):
        id_destr = GLib.timeout_add_seconds(
            timeout,
            self.destroy,
        )
        dinfo = _DestroyInfo(id_destr, timeout)
        _log.debug('Scheduling widget.destroy: {}'.format(dinfo))
        self._scheduled_destroyers.add(dinfo)
        return dinfo

    @classmethod
    def next_win_id(cls):
        cls.win_id += 1
        return cls.win_id

    @property
    def monitor_geometry(self):
        try:
            return self._monitor_geometry
        except AttributeError:
            self._monitor_geometry = monitor_geometry()
            return self._monitor_geometry
