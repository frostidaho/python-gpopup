import argparse
import logging

from gpopup import notifier
from gpopup.utils import get_app_logger


DEBUG = True
logger = get_app_logger(debug=DEBUG)

def server_parser():
    parser = argparse.ArgumentParser(description='GPopupServer Server.')
    parser.add_argument('--force-bind', action='store_true')
    parser.add_argument('--background', action='store_true')
    return parser

def main(args=None):
    parser = server_parser()
    args = parser.parse_args(args=args)
    logger.debug('force_bind = {}'.format(args.force_bind))
    serv = notifier.NotifierServer(force_bind=args.force_bind)
    try:
        serv.run(background=args.background)
    except KeyboardInterrupt:
        print('Got keyboard quit.', flush=True)
        # http://tldp.org/LDP/abs/html/exitcodes.html
        return 130
    return 0

