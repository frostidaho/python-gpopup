"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mgpopup` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``gpopup.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``gpopup.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
import argparse
from gpopup import notifier
from gpopup.message_parsers import Parse
from gpopup.window_utils import Position
import fileinput
import sys


SOCKET_NAME = 'gpopup/socket'

DEBUG = True

if DEBUG:
    import logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    try:
        from colorlog import ColoredFormatter
        frmt = ColoredFormatter(
            ('%(asctime)s @ %(log_color)s%(levelname)-8s%(reset)s @ '
             '%(module)s.%(funcName)s\n\t%(message)s'),
            datefmt="%H:%M:%S",
            reset=True,
            log_colors={
                'DEBUG':    'cyan',
                'INFO':     'green',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'red,bg_white',
            },
        )
    except ImportError:
        frmt = logging.Formatter(
            ('%(asctime)s @ %(levelname)s @ '
             '%(module)s.%(funcName)s\n\t%(message)s'),
            datefmt="%H:%M:%S",
        )
    handler.setFormatter(frmt)
    logger.addHandler(handler)


def main_parser():
    parser = argparse.ArgumentParser(description='Command description.')
    parser.add_argument('file', metavar='FILE', nargs=argparse.ZERO_OR_MORE,
                        help=("named input FILEs for lines containing a match"
                              " to the given PATTERN.  If no files are specified,"
                              " or if the file “-” is given, "
                              "the standard input is used."))
    parser.add_argument(
        '--parser',
        default=Parse.choices[0],
        choices=Parse.choices,
        help="Parser for FILEs",
    )
    parser.add_argument(
        '--position',
        default=Position.choices[0],
        choices=Position.choices,
        help="the position",
    )
    return parser

def read_files(file_names):
    contents_of_files = []
    if file_names:
        for fname in file_names:
            if fname == '-':
                contents_of_files.append(sys.stdin.read())
                continue
            with open(fname, 'r') as msg_file:
                contents_of_files.append(msg_file.read())
    else:
        contents_of_files.append(sys.stdin.read())
    return contents_of_files


def main(args=None):
    parser = main_parser()
    args = parser.parse_args(args=args)
    messages = read_files(args.file)

    msg_parser = getattr(Parse, args.parser)
    formatted_msgs = [msg_parser(x) for x in messages]

    windows = [notifier.MainWindow(x) for x in formatted_msgs]
    for win in windows:
        win.position = args.position
    notifier.gtk.main()

def client_parser():
    parser = argparse.ArgumentParser(description='Command description.')
    parser.add_argument('file', metavar='FILE', nargs=argparse.ZERO_OR_MORE,
                        help=("named input FILEs for lines containing a match"
                              " to the given PATTERN.  If the file “-” is given,"
                              "the standard input is used."))
    parser.add_argument(
        '--parser',
        default=Parse.choices[0],
        choices=Parse.choices,
        help="Parser for FILEs",
    )
    parser.add_argument(
        '--position',
        default=Position.choices[0],
        choices=Position.choices,
        help=("Set window position for new notification windows"
              ", and for the --move command."),
    )
    parser.add_argument(
        '-k', '--kill-server',
        action='store_true',
        help="Kill the server and exit"
    )
    parser.add_argument(
        '--start-server-maybe',
        action='store_true',
        help="Start the server if one is not already running."
    )
    parser.add_argument(
        '-id', '--notification-id',
        type=int,
        default=0,
        help=("The integer notification window id. If none is given it "
              "defaults to the last created and living window"),
        metavar='ID'
    )
    grp = parser.add_mutually_exclusive_group()
    grp.add_argument(
        '--hide',
        action='store_true',
        help="Hide the notification window ID"
    )
    grp.add_argument(
        '--show',
        action='store_true',
        help="Show the notification window ID"
    )
    grp.add_argument(
        '--destroy',
        action='store_true',
        help="Destroy the notification window ID"
    )

    parser.add_argument(
        '--move',
        action='store_true',
        help="Move window ID to POSITION"
    )
    parser.add_argument(
        '--timeout',
        type=float,
        help="Make notification ID timeout after TIMEOUT",
    )
    return parser

def main_client(args=None):
    parser = client_parser()

    args = parser.parse_args(args=args)
    wid = args.notification_id
    wid = wid if wid else None

    client = notifier.NotifierClient(SOCKET_NAME)
    if args.kill_server:
        client.kill_server()
        return
    if args.start_server_maybe:
        client.start_server_maybe()

    if args.file:
        messages = read_files(args.file)
        msg_parser = getattr(Parse, args.parser)
        formatted_msgs = [msg_parser(x) for x in messages]
        win_ids = [client.new_window(x, position=args.position) for x
                   in formatted_msgs]
        print('Created windows:', win_ids)

    wid_cmds = ['hide', 'show', 'destroy']
    for cmd in wid_cmds:
        if getattr(args, cmd):
            getattr(client, cmd)(notification_id=wid)

    if args.move:
        client.movewin(position=args.position, notification_id=wid)

    if args.timeout:
        client.timeout(timeout=args.timeout, notification_id=wid)
    return True


def server_parser():
    parser = argparse.ArgumentParser(description='GPopupServer Server.')
    parser.add_argument('--force-bind', action='store_true')
    parser.add_argument('--background', action='store_true')
    return parser


def main_server(args=None):
    parser = server_parser()
    args = parser.parse_args(args=args)
    print('force_bind = ', args.force_bind)
    serv = notifier.NotifierServer(SOCKET_NAME, args.force_bind)
    try:
        serv.run(background=args.background)
    except KeyboardInterrupt:
        print('Got keyboard quit.', flush=True)
