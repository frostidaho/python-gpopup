from gpopup.utils import format_tbl_msg as _format_tbl_msg
import gpopup.message_widgets as _widgets
from collections import (namedtuple as _namedtuple,
                         OrderedDict as _OrderedDict,
                         UserList as _UserList)
# import xml.etree.ElementTree as _ElementTree
# from io import StringIO as _StringIO
import json as _json
# import inspect as _inspect
# import functools as _functools


class ParseError(Exception):
    pass

choices = _OrderedDict()


class MetaRegister(type):

    def __new__(meta, clsname, bases, attrs):
        newcls = super().__new__(meta, clsname, bases, attrs)
        if clsname != 'BaseMessage':
            choices[clsname] = newcls
        return newcls


class BaseMessage(metaclass=MetaRegister):
    export_attrib = ['body']
    _widget_type = None

    def __init__(self, **kwargs):
        self.widget_opts = kwargs.pop('widget_opts', {})
        self.widget_opts.update(kwargs)

    @property
    def msg_type(self):
        return self.__class__.__name__

    @classmethod
    def from_html(cls, html_string, *pargs, **kwargs):
        import xml.etree.ElementTree as _ElementTree
        try:
            return cls(**cls._from_html(html_string, *pargs, **kwargs))
        except _ElementTree.ParseError:
            raise ParseError("Couldn't parse as html")

    @classmethod
    def from_json(cls, json_string, **kwargs):
        try:
            return cls(**cls._from_json(json_string, **kwargs))
        except _json.decoder.JSONDecodeError as e:
            raise ParseError("Couldn't parse as json")

    @staticmethod
    def _from_json(json_string, **kwargs):
        jmsg = _json.loads(json_string)
        if isinstance(jmsg, dict):
            dmsg = jmsg
        else:
            raise ValueError('JSON data must be a dictionary')
        dmsg.update(kwargs)
        return dmsg

    @classmethod
    def from_text(cls, txt_string, *pargs, **kwargs):
        return cls(**cls._from_text(txt_string, *pargs, **kwargs))

    @classmethod
    def from_inst_dict(cls, inst_dict):
        new = cls.__new__(cls)
        new.__dict__.update(inst_dict)
        return new

    def get_widget(self):
        return self._widget_type(self)

    @property
    def as_dict(self):
        d = {x: getattr(self, x) for x in self.export_attrib}
        d['msg_type'] = self.msg_type
        d['widget_opts'] = getattr(self, 'widget_opts', {})
        return d

    def __repr__(self):
        d = self.as_dict
        clsname = d.pop('msg_type')
        return '{}(**{})'.format(clsname, d)


class Simple(BaseMessage):
    export_attrib = ['summary', 'body']
    _widget_type = _widgets.SimpleWidget

    def __init__(self, summary='', body='', **kwargs):
        super().__init__(**kwargs)
        self.summary = summary.strip()
        self.body = body.strip()

    def _from_text(txt_string, row_sep='\n', *pargs, **kwargs):
        msg = txt_string.split(row_sep, maxsplit=1)
        if len(msg) > 1:
            dmsg = {'summary': msg[0], 'body': msg[1]}
        elif len(msg) == 1:
            dmsg = {'summary': msg[0]}
        else:
            dmsg = {'summary': txt_string}
        dmsg.update(kwargs)
        return dmsg


_TextTag = _namedtuple('_TextTag', 'text tag')


class Table(BaseMessage):
    export_attrib = ['body', 'columns']
    _widget_type = _widgets.TableWidget

    def __init__(self, body='', columns=(), **kwargs):
        super().__init__(**kwargs)
        self.body, self.columns = _format_tbl_msg(
            message=body,
            columns=columns,
        )

    @staticmethod
    def _from_html(html_string, *pargs, **kwargs):
        def _transform_html_row(row):
            return tuple(_TextTag(''.join(x.itertext()), x.tag) for x in row)
        import xml.etree.ElementTree as _ElementTree
        from io import StringIO as _StringIO
        html_file = _StringIO(html_string)
        tree = _ElementTree.parse(html_file)
        rows = tree.getiterator('tr')
        cols = ()
        new_rows = []
        for i, row in enumerate(rows):
            row = _transform_html_row(row)
            if i == 0:
                if all(x.tag == 'th' for x in row):
                    cols = tuple(x.text for x in row)
                    continue
            new_rows.append(tuple(x.text for x in row))
        dmsg = {'body': tuple(new_rows), 'columns': cols}
        dmsg.update(kwargs)
        return dmsg

    @classmethod
    def from_text(cls, txt_string, col_sep='\t', row_sep='\n',
                  mark_header='###', *pargs, **kwargs):
        return cls(
            **cls._from_text(
                txt_string,
                col_sep=col_sep,
                row_sep=row_sep,
                mark_header=mark_header,
            ),
            **kwargs,
        )

    @staticmethod
    def _from_text(txt_string, col_sep='\t', row_sep='\n',
                   mark_header='###', *pargs, **kwargs):
        cols = ()
        rows = []
        for row in txt_string.strip().split(row_sep):
            row = row.strip()
            if not row:             # Skip empty rows
                continue
            if mark_header in row:
                cols = row.replace(mark_header, '')
                cols = [x.strip() for x in cols.split(col_sep)]
                continue
            rows.append([x.strip() for x in row.split(col_sep)])
        return {'body': rows, 'columns': cols}


def make_msg(msg_type='Simple', **msg_keywords):
    # TODO Remove and replace with the Messages class (new_messages())
    msg_type = msg_keywords.pop('msg_type', msg_type)
    if isinstance(msg_type, str):
        Msg = choices[msg_type]
    else:
        Msg = msg_type
    return Msg(**msg_keywords)


def _add_messages(cls):
    import inspect as _inspect
    import functools as _functools
    def add_msg_method(Msg):
        sig = _inspect.signature(Msg)
        pself = _inspect.Parameter('self', _inspect.Parameter.POSITIONAL_OR_KEYWORD)
        sig2 = _inspect.Signature([pself] + list(sig.parameters.values()))
        @_functools.wraps(Msg)
        def wrapper(self, *pargs, **kwargs):
            out = Msg(*pargs, **kwargs)
            self.append(out)
            return out
        wrapper.__signature__ = sig2
        return wrapper

    for k,v in choices.items():
        setattr(cls, k, add_msg_method(v))
    return cls


# @_add_messages
class _Messages(_UserList):
    def make_window(self):
        window = _widgets.MainWindow(*self.data)
        # self.window = window
        return window

    def run_blocking(self):
        _widgets.Gtk.main()

def new_messages():
    global _Messages
    _Messages = _add_messages(_Messages)
    return _Messages()
