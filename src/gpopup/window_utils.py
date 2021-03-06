import logging as _logging
from collections import OrderedDict, namedtuple

from gpopup.utils import OrderedChoices

_log = _logging.getLogger(__name__)
_log.addHandler(_logging.NullHandler())

BORDER_THICKNESS = 4            # pixels

MoveResize = namedtuple('MoveResize', 'x y width height')
MonitorGeometry = namedtuple(
    'MonitorGeometry',
    ['left', 'right', 'top', 'bottom', 'width', 'height'],
)


def monitor_geometry():
    """monitor_geometry() returns info about the monitor of the focused window.

    This function requires the Gdk 3.0 bindings
    Returns:
       A named tuple containing ints which describe the extents of the monitor.
       The tuple's fields left, right, top, and bottom are the *absolute* pixel
       location of the monitor's corresponding sides. Width and height are the
       monitor's width and height in pixels.

       MonitorGeometry(left, right, top, bottom, width, height)
    """
    # It's important to import Gdk inside this code for testing purposes
    import gi
    gi.require_version('Gdk', '3.0')
    from gi.repository import Gdk
    display = Gdk.Display.get_default()
    screen = display.get_default_screen()
    debug = _log.debug

    def _get_geom():
        window = screen.get_active_window()  # returns None if no active window
        if window is not None:
            debug('Screen has no active window')
            monitor = screen.get_monitor_at_window(window)
            return screen.get_monitor_geometry(monitor)
        try:
            return display.get_primary_monitor().get_geometry()
        except AttributeError:
            debug('Display has no primary monitor')
            return display.get_monitor(0).get_geometry()
    g = _get_geom()

    right = g.x + g.width
    bottom = g.y + g.height
    geom = MonitorGeometry(g.x, right, g.y, bottom, g.width, g.height)
    debug('Monitor geometry is {!r}'.format(geom))
    return geom


class Position(metaclass=OrderedChoices):
    def __init__(self, x, y, width, height):
        self.mon_geom = monitor_geometry()
        # self.geom = MoveResize(x, y, width, height)
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    @property
    def center(self):
        return MoveResize(self._xval(1), self._yval(1), self.width, self.height)

    @property
    def northwest(self):
        return MoveResize(self._xval(0), self._yval(0), self.width, self.height)

    @property
    def north(self):
        return MoveResize(self._xval(1), self._yval(0), self.width, self.height)

    @property
    def northeast(self):
        return MoveResize(self._xval(2), self._yval(0), self.width, self.height)

    @property
    def west(self):
        return MoveResize(self._xval(0), self._yval(1), self.width, self.height)

    @property
    def east(self):
        return MoveResize(self._xval(2), self._yval(1), self.width, self.height)

    @property
    def southwest(self):
        return MoveResize(self._xval(0), self._yval(2), self.width, self.height)

    @property
    def south(self):
        return MoveResize(self._xval(1), self._yval(2), self.width, self.height)

    @property
    def southeast(self):
        return MoveResize(self._xval(2), self._yval(2), self.width, self.height)

    def _xval(self, position):
        "pos = 0 on left, 1 on middle, or 2 on right"
        mon_geom = self.mon_geom
        if position == 0:
            return mon_geom.left
        elif position == 1:
            mon_ctr_x = (mon_geom.left + mon_geom.right) // 2
            return mon_ctr_x - (self.width // 2)
        elif position == 2:
            return mon_geom.right - self.width - (2 * BORDER_THICKNESS)
        raise ValueError('position must be 0, 1, or 2')

    def _yval(self, position):
        "pos = 0, 1 or 2"
        mon_geom = self.mon_geom
        if position == 0:
            return mon_geom.top
        elif position == 1:
            mon_ctr_y = (mon_geom.top + mon_geom.bottom) // 2
            return mon_ctr_y - (self.height // 2)
        elif position == 2:
            return mon_geom.bottom - self.height - (2 * BORDER_THICKNESS)
        raise ValueError('position must be 0, 1, or 2')
