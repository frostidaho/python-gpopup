import argparse

import gpopup.message_types as mtypes
import gpopup.message_widgets as mwidgets
from gpopup.utils import read_files, get_app_logger
from gpopup.window_utils import Position

DEBUG = True
logger = get_app_logger(debug=DEBUG)

def main_parser():
    parser = argparse.ArgumentParser(description='Command description.')
    parser.add_argument('file', metavar='FILE', nargs=argparse.ZERO_OR_MORE,
                        help=("named input FILEs for lines containing a match"
                              " to the given PATTERN.  If no files are specified,"
                              " or if the file “-” is given, "
                              "the standard input is used."))
    parser.add_argument(
        '--position',
        default=Position.choices[0],
        choices=Position.choices,
        help="the position",
    )
    return parser

def main(args=None):
    parser = main_parser()
    args = parser.parse_args(args=args)
    messages = read_files(args.file)

    formatted_msgs = []
    tab = mtypes.Table
    table_factories = [tab.from_json, tab.from_html, tab.from_text]
    for msg in messages:
        for fac in table_factories:
            try:
                formatted_msgs.append(fac(msg))
                break
            except mtypes.ParseError:
                continue
        else:
            raise mtypes.ParseError("No parsing method was successful")
    win = mwidgets.MainWindow(*formatted_msgs)
    win.position = args.position
    mwidgets.Gtk.main()
