import json
import logging as _logging
import os
import pickle
import socket
import struct
import sys
import traceback
from collections import namedtuple as _namedtuple
from functools import wraps as _wraps
from pprint import pformat as _pformat
from time import sleep as _sleep
from time import time as _time

from gi.repository import GLib

_log = _logging.getLogger(__name__)
_log.addHandler(_logging.NullHandler())
# TODO replace _debug with something else or fix it
# in the log records _debug shows up as the calling function


def _debug(*pargs):
    formatted = (_pformat(x) for x in pargs)
    return _log.debug('\n\t'.join(formatted))


_DEFAULT_CONN_TIMEOUT = 0.2
_SMALL_EPSILON = 1.0e-6
_SerialMsg = _namedtuple('_SerialMsg', 'type message')
_MsgHeader = _namedtuple('_MsgHeader', 'type length')
_HEADER_FMT = '!20sQ'
_HEADER_FMT_SIZE = struct.calcsize(_HEADER_FMT)
_KILL_SERVER_HEADER = ('kill', 0)

_CmdError = _namedtuple('_CmdError', 'exception text')


def _strs_to_uuid(*strs):
    "Return a UUID from any number of strings"
    from uuid import UUID
    from hashlib import md5
    md5sum = md5()
    total = '.'.join(strs).encode()
    md5sum.update(total)
    return UUID(bytes=md5sum.digest())


def _obj_to_uuid(obj):
    """Create a UUID given an object.

    The UUID is made from the object's __module__ and __name__ properties
    """
    return _strs_to_uuid(obj.__module__, obj.__name__)


def _pack_header(msg_type='', length=0):
    msg_type = msg_type.encode()
    return struct.pack(_HEADER_FMT, msg_type, length)


def _unpack_header(header_bytes):
    msg_type, length = struct.unpack(_HEADER_FMT, header_bytes)
    msg_type = msg_type.decode().replace('\x00', '')
    return _MsgHeader(msg_type, length)


class Marshall:
    """Marshall provides facilities to serialize and deserialize objects.

    It is inherited by Server and BaseClient classes.
    """
    serial_method = 'pickle'

    @staticmethod
    def _serialize_pickle(py_obj):
        "Return a tuple of ('pickle', bytes string) from a python object"
        return _SerialMsg('pickle', pickle.dumps(py_obj))

    @staticmethod
    def _deserialize_pickle(data):
        "Return python object from a pickle bytes string"
        return pickle.loads(data)

    @staticmethod
    def _serialize_json(py_obj):
        "Return a tuple of ('json', bytes string) from a python object"
        return _SerialMsg('json', json.dumps(py_obj).encode())

    @staticmethod
    def _deserialize_json(data):
        "Return python object from json bytes string"
        return json.loads(data.decode())

    @classmethod
    def receive_obj(cls, conn):
        """Return some python object from socket connection conn

        If no valid message header is received it returns None.
        """
        header_bytes = conn.recv(_HEADER_FMT_SIZE)
        try:
            msg_header = _unpack_header(header_bytes)
        except struct.error:
            _debug('Received no header')
            return None
        if msg_header == _KILL_SERVER_HEADER:
            _debug('Received _KILL_SERVER_HEADER')
            return _KILL_SERVER_HEADER
        data = conn.recv(msg_header.length)
        return getattr(cls, '_deserialize_{}'.format(msg_header.type))(data)

    def send_obj(self, conn, py_obj):
        """Send py_obj over socket connection conn.

        It uses the serialization method self.serial_method
        """
        serializer = getattr(self, '_serialize_{}'.format(self.serial_method))
        stype, message_bytes = serializer(py_obj)
        header = _pack_header(stype, len(message_bytes))
        try:
            conn.send(header)
            conn.sendall(message_bytes)
        except BrokenPipeError:
            _debug('Could not send - connection closed.')


def _run_with_timeout(target, *pargs,
                      tmax=2.0, delta_t0=0.04, delta_t_max=0.2,
                      swallow=(ConnectionRefusedError, FileNotFoundError),
                      fail_raise=ConnectionError,
                      **kwargs):
    """Try to run the callable target(*pargs, **kwargs) until time tmax

    If the callable does not raise an exception its return value is returned.
    If no value is returned within the timelimit raise Exception.
    """
    if tmax <= _SMALL_EPSILON:
        try:
            return target(*pargs, **kwargs)
        except swallow as e:
            raise ConnectionError(e.args)
    t_end = _time() + tmax
    delta_t = delta_t0
    while _time() <= t_end:
        try:
            return target(*pargs, **kwargs)
        except swallow:
            pass
        _sleep(delta_t)
        delta_t = min(1.2 * delta_t, delta_t_max)
    else:
        raise ConnectionError('Timeout expired')


class SocketInfo:

    def __init__(self, sock_name, server=True, timeout=0.0, force_bind=False):
        self.sock_name = sock_name
        self.server = server
        self.force_bind = force_bind
        self.timeout = timeout

    def get_sock(self):
        if self.server:
            return self._get_server_socket(self.sock_path, self.timeout, self.force_bind)
        return self._get_client_socket(self.sock_path, self.timeout)

    @property
    def sock_path(self):
        "Return the complete path for the unix-socket called self.sock_name"
        env = os.environ.get
        for base_dir in map(env, ['XDG_RUNTIME_DIR', 'XDG_CACHE_HOME']):
            if base_dir:
                break
        if not base_dir:
            base_dir = os.path.expanduser('~/.cache/')
        return os.path.join(base_dir, 'gpopup_ipc', self.sock_name)

    @staticmethod
    def _sock_bind(file_path):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            os.remove(file_path)
        except (OSError, FileNotFoundError):
            if os.path.exists(file_path):
                raise
        try:
            sock.bind(file_path)
        except FileNotFoundError:
            os.makedirs(os.path.dirname(file_path), mode=0o700, exist_ok=True)
            sock.bind(file_path)
        sock.listen(1)
        return sock

    @classmethod
    def _get_server_socket(cls, file_path, timeout, force_bind):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            conn = cls._get_client_socket(file_path, timeout)
        except ConnectionError:
            sock = cls._sock_bind(file_path)
            return sock

        if not force_bind:
            _debug('Connected to server - not starting')
            return None

        _debug('Found already running server - shutting down')
        conn.send(_pack_header(*_KILL_SERVER_HEADER))
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()
        sock = cls._sock_bind(file_path)
        return sock

    @staticmethod
    def _get_client_socket(file_path, timeout):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        _run_with_timeout(sock.connect, file_path, tmax=timeout)
        return sock


class Server(Marshall):
    """The Server class can be subclassed and extended with commands

    which are methods that are named cmd_XXX.
    For example:
    def cmd_echo(self, *pargs, **kwargs):
        "Echo pargs and kwargs back"
        return (pargs, kwargs)

    An associated client class is returned by calling Server.get_client().
    Client = Server.get_client()
    client = Client()
    serv = Server()
    # serv.run()              #  blocking
    serv.run(background=True) #  non-blocking uses fork
    out = client.echo(1,2,3, x='x string', y={'a': True})
    # out == ((1, 2, 3), {'x': 'x string', 'y': {'a': True}})
    """
    _conn_timeout = _DEFAULT_CONN_TIMEOUT

    def __init__(self, sock_name='', force_bind=False):
        if sock_name:
            self.sock_name = sock_name
        self.loop = GLib.MainLoop()
        self.force_bind = force_bind
        self.sock_info = SocketInfo(
            self.sock_name,
            server=True,
            timeout=self._conn_timeout,
            force_bind=force_bind,
        )

    @classmethod
    def _default_sock_name(cls):
        try:
            return cls.__sock_uuid
        except AttributeError:
            uuid = str(_obj_to_uuid(cls))
            cls.__sock_uuid = uuid
            return uuid

    @property
    def sock_name(self):
        try:
            return self._sock_name
        except AttributeError:
            return self._default_sock_name()

    @sock_name.setter
    def sock_name(self, value):
        self._sock_name = value

    @sock_name.deleter
    def sock_name(self):
        del self._sock_name

    @classmethod
    def get_client(cls):
        docstr = """\
        Associated client for the server {}
        """.format(cls.__name__)

        class Client(BaseClient):
            command_server = cls
        Client.__doc__ = docstr
        return Client

    def _watch_sock(self):
        self.sock_info.timeout = self._conn_timeout
        sock = self.sock_info.get_sock()
        if sock is None:
            return False
        else:
            self.sock = sock
        _debug('Adding socket callbacks to GLib loop')
        GLib.io_add_watch(
            self.sock,
            GLib.PRIORITY_DEFAULT,
            GLib.IO_IN,
            self._socket_rdy,
        )

        # GLib.IO_HUP is the hangup condition
        # i.e., if another server deletes or binds to the same socket path
        # Maybe?? I'm not sure if this works as expected.
        # https://developer.gnome.org/pygobject/stable/glib-functions.html#function-glib--io-add-watch
        GLib.io_add_watch(
            self.sock,
            GLib.PRIORITY_DEFAULT,
            GLib.IO_HUP,
            self._loop_quit,
        )
        return True

    def _loop_run(self):
        self.loop.run()

    def _loop_quit(self, *pargs, **kwargs):
        self.loop.quit()

    def run(self, background=False):
        """Start the server.

        By default it is a blocking operation.
        However, if background=True then the server will be forked
        and execution in the main program will continue.

        The value of self.force_bind determines whether run()
        will kick off any other server process that is bound
        to the socket.
        """
        # http://stackoverflow.com/a/1603152
        # Calling self._watch_sock() may open a socket
        # for this reason, it's probably best to call
        # this after a call to fork.
        if background:
            fpid = os.fork()
            if fpid == 0:
                try:
                    if self._watch_sock():
                        self._loop_run()
                finally:
                    os._exit(0)
                    # sys.exit(0)
            elif fpid == -1:    # elif fork failed
                os._exit(1)
                # sys.exit(1)
            else:
                return None
        else:
            if self._watch_sock():
                self._loop_run()
                return True
            return False

    def _handle_message(self, message_obj):
        cmd_name = message_obj['cmd_name']
        pargs = message_obj['pargs']
        kwargs = message_obj['kwargs']
        # _debug('Server received message for command {}'.format(cmd_name), pargs, kwargs)
        _debug('Server received message for command {}'.format(cmd_name))
        try:
            res = getattr(self, 'cmd_{}'.format(cmd_name))(*pargs, **kwargs)
        except Exception as e:
            _log.info('Running cmd_{} on server failed'.format(cmd_name))
            # traceback.print_exception(type(e), e, e.__traceback__)
            ex_txt = traceback.format_exception(type(e), e, e.__traceback__)
            ex_txt = ''.join(ex_txt)
            _log.info(ex_txt)
            res = _CmdError(e, ex_txt)
        return res

    def _socket_rdy(self, sock, cond):
        conn, client_address = sock.accept()

        obj = self.receive_obj(conn)
        if obj == _KILL_SERVER_HEADER:
            self.cmd_kill_server()
            return False
        elif obj is None:
            return True
        out = self._handle_message(obj)
        self.send_obj(conn, out)
        conn.close()            # Might as well close conn on server side
        return True

    def cmd_ping(self, *pargs, **kwargs):
        "Ping the server; returns True"
        return True

    def cmd_echo(self, *pargs, **kwargs):
        "Echo pargs and kwargs back"
        return (pargs, kwargs)

    def cmd_kill_server(self, *pargs, **kwargs):
        "Kill server and main loop"
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        self._loop_quit()


class AddCommands:
    """Decorator for adding commands to a client class.

    Assumes that the client class implements a method
    run_cmd(self, cmd, *pargs, **kwargs)

    where cmd is the command name without the leading 'cmd_'
    """

    def __init__(self, command_class):
        self.command_class = command_class

    def __call__(self, client_class):
        cmds = [x for x in dir(self.command_class) if x.startswith('cmd_')]
        cmds = [x.replace('cmd_', '') for x in cmds]

        def create_method(cmd):
            @_wraps(getattr(self.command_class, 'cmd_' + cmd))
            def run_specific_cmd(self, *pargs, **kwargs):
                return self.run_cmd(cmd, *pargs, **kwargs)
            return run_specific_cmd
        d_cmds = {cmd: create_method(cmd) for cmd in cmds}
        for cmd, method in d_cmds.items():
            setattr(client_class, cmd, method)
        setattr(client_class, 'commands', sorted(d_cmds))
        return client_class


class MetaClient(type):
    """MetaClient adds commands to a client class.

    It looks at the commands defined on the command server
    pointed to by the command_server attribute
    """
    def __new__(meta, name, bases, clsdict):
        cls = type.__new__(meta, name, bases, clsdict)
        server = clsdict.get('command_server', None)
        if server is not None:
            cls = AddCommands(server)(cls)
        # maybe fold this next bit into the previous
        # if block, but note that clsdict['attr'] and cls.attr
        # are not equivalent
        server = cls.command_server
        if server is not None:
            cls.sock_name = server._default_sock_name()
            cls.serial_method = server.serial_method
        return cls


class BaseClient(Marshall, metaclass=MetaClient):
    """Create client classes by subclassing BaseClient

    Don't try to use this class directly; It won't work.

    set the command_server attribute in the subclasses body
    to be a command server class.
    """
    command_server = None
    _conn_timeout_long = _DEFAULT_CONN_TIMEOUT * 2.0
    _conn_timeout = _DEFAULT_CONN_TIMEOUT

    def __init__(self, sock_name=''):
        if sock_name:
            self.sock_name = sock_name
        self._sock_info = SocketInfo(
            self.sock_name,
            server=False,
            timeout=self._conn_timeout,
        )

    def run_cmd(self, cmd_name, *pargs, **kwargs):
        d_message = {
            'cmd_name': cmd_name,
            'pargs': pargs,
            'kwargs': kwargs,
        }
        # _debug('Running command: {}'.format(cmd_name), pargs, kwargs)
        _debug('Running command: {}'.format(cmd_name))

        try:
            self._sock_info.timeout = self._conn_timeout
            sock = self._sock_info.get_sock()
        except ConnectionError:
            self._sock_info.timeout = self._conn_timeout_long
            sock = self._sock_info.get_sock()
        finally:
            self._sock_info.timeout = self._conn_timeout

        try:
            self.send_obj(sock, d_message)
            recv = self.receive_obj(sock)
        finally:
            sock.close()
        if isinstance(recv, _CmdError):
            _log.info('Error running command: {}'.format(cmd_name))
            _log.info(recv.text)
            raise recv.exception
        return recv

    def start_server_maybe(self):
        orig_timeout = self._conn_timeout
        try:
            self.ping()
            _log.debug('Server already running - do not need to start')
        except ConnectionError:
            self._conn_timeout = self._conn_timeout_long
            serv = self.command_server(sock_name=self.sock_name)
            serv.run(background=True)
            _log.debug('Server is not already running - starting in a child process')
            self.ping()
        finally:
            self._conn_timeout = orig_timeout
