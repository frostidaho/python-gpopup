from itertools import (
    islice as _islice,
    chain as _chain,
)
from collections import (namedtuple as _namedtuple,
                         OrderedDict as _OrderedDict)
import sys as _sys
import logging as _logging

class OrderedChoices(type):
    @classmethod
    def __prepare__(self, name, bases):
        return _OrderedDict()

    def __new__(self, name, bases, classdict):
        classdict['choices'] = tuple(key for key in classdict.keys()
                                if not key.startswith('_'))
        return type.__new__(self, name, bases, classdict)


def message_depth(msg, maxdepth=2, n=0):
    if isinstance(msg, str):
        return n
    elif n >= maxdepth:
        return maxdepth
    else:
        try:
            return message_depth(next(iter(msg)), maxdepth, n + 1)
        except TypeError:
            # If element is not an iterable type
            return n


def takeall(n, iterable):
    iterable = iter(iterable)
    def take(n, iterable):
        "Return first n items of the iterable as a tuple"
        return tuple(_islice(iterable, n))

    while True:
        x = take(n, iterable)
        if x:
            yield x
        else:
            return

def ensure_row_length(matrix, ncols, fill=''):
    """Make sure each row in matrix has length ncols.

    If a row's length is less than ncols add elements fill
    Returns a 2d tuple
    """
    tcols = (fill,) * ncols
    return tuple(tuple(_islice(_chain(x, tcols), ncols)) for x in matrix)

def vector_to_matrix(vector, ncols=1, fill=''):
    """Reshape the 1d vector into a 2d matrix

    The returned matrix has ncols number of columns.
    If the length of the vector is such that the number of columns
    can not be filled exactly, the additional elements are given by
    fill.
    """
    mat = takeall(ncols, vector)
    return ensure_row_length(mat, ncols, fill)


FormattedTblMsg = _namedtuple('FormattedTblMsg', 'entries columns')
def format_tbl_msg(message='', columns=()):
    mdepth = message_depth(message)
    if isinstance(columns, int):
        columns = columns * ('',)
    elif not columns:
        if mdepth < 2: # i.e., msg is a string or a vector
            columns = ('',)
        else:
            columns = len(max(message, key=lambda x: len(x))) * ('',)

    if mdepth == 0:
        message = ((message,),)
        message = ensure_row_length(message, ncols=len(columns))
    elif mdepth == 1:
        message = vector_to_matrix(message, ncols=len(columns))
    elif mdepth == 2:
        message = ensure_row_length(message, ncols=len(columns))
    return FormattedTblMsg(message, columns)


def read_files(file_names):
    contents_of_files = []
    if file_names:
        for fname in file_names:
            if fname == '-':
                contents_of_files.append(_sys.stdin.read())
                continue
            with open(fname, 'r') as msg_file:
                contents_of_files.append(msg_file.read())
    else:
        contents_of_files.append(_sys.stdin.read())
    return contents_of_files


def get_app_logger(debug=True):
    LOGGER_NAME = 'gpopup'
    if debug:
        logger = _logging.getLogger(LOGGER_NAME)
        logger.setLevel(_logging.DEBUG)
        handler = _logging.StreamHandler()
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
            frmt = _logging.Formatter(
                ('%(asctime)s @ %(levelname)s @ '
                 '%(module)s.%(funcName)s\n\t%(message)s'),
                datefmt="%H:%M:%S",
            )
        handler.setFormatter(frmt)
        logger.addHandler(handler)
    else:
        logger = _logging.getLogger(LOGGER_NAME)
        logger.addHandler(_logging.NullHandler())
    return logger
