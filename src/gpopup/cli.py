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
from gpopup import (notifier, message_parsers)
import fileinput
import sys

msg_parsers = message_parsers.choices

parser = argparse.ArgumentParser(description='Command description.')
parser.add_argument('file', metavar='FILE', nargs=argparse.ZERO_OR_MORE,
                    help="named input FILEs for lines containing a match to the given PATTERN.  If no files are specified, or if the file “-” is given, the standard input is used.")
parser.add_argument(
    '--parser',
    choices=msg_parsers,
    help="Parser for FILEs",
)

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
    args = parser.parse_args(args=args)
    messages = read_files(args.file)

    msg_parser = msg_parsers[args.parser]
    formatted_msgs = [msg_parser(x) for x in messages]

    windows = [notifier.get_window(x) for x in formatted_msgs]
    notifier.gtk.main()
    
