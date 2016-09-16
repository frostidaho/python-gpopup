import xml.etree.ElementTree as _ElementTree
import json as _json
from io import StringIO as _StringIO
from collections import (namedtuple as _namedtuple,)
from gpopup import utils as _utils

_TextTag = _namedtuple('_TextTag', 'text tag')

def _transform_html_row(row):
    # return tuple(_TextTag(''.join(list(x.itertext())), x.tag) for x in row)
    return tuple(_TextTag(''.join(x.itertext()), x.tag) for x in row)

def html_to_2d_tuple(html_string):
    html_file = _StringIO(html_string)
    tree = _ElementTree.parse(html_file)
    rows = tree.getiterator('tr')
    cols = ()
    new_rows = []
    for i,row in enumerate(rows):
        row = _transform_html_row(row)
        if i == 0:
            if all(x.tag == 'th' for x in row):
                cols = tuple(x.text for x in row)
                continue
        new_rows.append(tuple(x.text for x in row))
    return _utils.format_tbl_msg(tuple(new_rows), columns=cols)

def json_to_2d_tuple(json_string):
    dat = _json.loads(json_string)
    cols = ()
    msg = ''
    if isinstance(dat, dict):
        cols = dat.get('columns', cols)
        msg = dat.get('message', msg)
    else:
        msg = dat
    return _utils.format_tbl_msg(msg, columns=cols)


def text_to_2d_tuple(txt_string, col_sep='\t', row_sep='\n',
                     mark_header='###'):
    cols = ()
    rows = []
    for row in txt_string.strip().split(row_sep):
        row = row.strip()
        if not row:             # Skip empty rows
            continue
        if mark_header in row:
            cols = row.replace(mark_header, '') #.strip()
            cols = [x.strip() for x in cols.split(col_sep)]
            continue
        rows.append([x.strip() for x in row.split(col_sep)])
    return _utils.format_tbl_msg(rows, columns=cols)


class Parse(metaclass=_utils.OrderedChoices):
    text = staticmethod(text_to_2d_tuple)
    json = staticmethod(json_to_2d_tuple)
    html = staticmethod(html_to_2d_tuple)
