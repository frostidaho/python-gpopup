import xml.etree.ElementTree as _ElementTree
from io import StringIO as _StringIO
from collections import (namedtuple as _namedtuple,
                         OrderedDict as _OrderedDict)
from gpopup import utils as _utils

_TextTag = _namedtuple('_TextTag', 'text tag')

def _transform_html_row(y):
    elems = list(y)
    return tuple(_TextTag(list(x.itertext())[0], x.tag) for x in elems)

def html_to_2d_tuple(html_string):
    html_file = _StringIO(html_string)
    tree = _ElementTree.parse(html_file)
    rows = tree.getiterator('tr')
    cols = ()
    new_rows = []
    for i,row in enumerate(rows):
        if i == 0:
            if all(x.tag == 'th' for x in row):
                cols = tuple(x.text for x in row)
                continue
        new_rows.append(tuple(x.text for x in row))
    return _utils.format_msg(tuple(new_rows), columns=cols)


choices = _OrderedDict((
    ('html', html_to_2d_tuple),
))
