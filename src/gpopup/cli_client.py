import argparse
import json
import sys

from gpopup.message_types import make_msg
from gpopup.notifier import NotifierClient
from gpopup.utils import get_app_logger
from gpopup.window_utils import Position

# SOCKET_NAME = 'gpopup/socket'
DEBUG = True
logger = get_app_logger(debug=DEBUG)


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


def client_parser():
    parser = argparse.ArgumentParser(description='Command description.')
    parser.add_argument('file', metavar='FILE', nargs=argparse.ZERO_OR_MORE,
                        help=("named input FILEs for lines containing a match"
                              " to the given PATTERN.  If the file “-” is given,"
                              "the standard input is used."))
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


def main(args=None):
    parser = client_parser()

    args = parser.parse_args(args=args)
    wid = args.notification_id
    wid = wid if wid else None

    client = NotifierClient()
    if args.kill_server:
        client.kill_server()
        return
    if args.start_server_maybe:
        client.start_server_maybe()

    if args.file:
        jmsges = [json.loads(x) for x in read_files(args.file)]
        msges = []
        for jmsg in jmsges:
            if isinstance(jmsg, list):
                msges.extend(jmsg)
            else:
                msges.append(jmsg)

        msges = [make_msg(**x) for x in msges]
        # formatted_msgs = [msg_parser(x) for x in messages]
        if msges:
            wid = client.new_window(*msges, position=args.position)
            logger.debug('Created window with id: {}'.format(wid))
            print(json.dumps({'notification_id': wid}))

    wid_cmds = ['hide', 'show', 'destroy']
    for cmd in wid_cmds:
        if getattr(args, cmd):
            getattr(client, cmd)(notification_id=wid)

    if args.move:
        client.movewin(position=args.position, notification_id=wid)

    if args.timeout:
        client.timeout(timeout=args.timeout, notification_id=wid)
    return 0
