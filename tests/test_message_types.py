import unittest
from gpopup import message_types
import json


class DictAndJson:
    def __init__(self, **kwargs):
        self.data = kwargs

    @property
    def json_string(self):
        return json.dumps(self.data)

def data_file(name):
    from os import path
    tests_dir = path.dirname(path.realpath(__file__))
    return path.join(tests_dir, 'data', name)

class MsgHelpers:
    def assertMsgEqual(self, msg1, msg2):
        self.assertEqual(msg1.__dict__, msg2.__dict__)
        self.assertEqual(msg1.as_dict, msg2.as_dict)

class TestTable(unittest.TestCase):
    "Test Table message type"
    @classmethod
    def setUpClass(cls):
        cls.msgtype = message_types.Table
        with open(data_file('faker_names.python'), 'rt') as faker_names:
            faker_dict = eval(faker_names.read())
        cls.faker_dict = faker_dict
        cls.msg = cls.msgtype(**cls.faker_dict)

    def test_choices(self):
        choice = message_types.choices[self.msgtype.__name__]
        self.assertEqual(choice, self.msgtype)

    def test_repr(self):
        msg = self.msgtype(body=['a', 'b', 'c'], columns=['Col 1', 'Col 2'], font_size=13)
        msg_from_repr = eval('message_types.' + repr(msg))
        self.assertEqual(msg.__dict__, msg_from_repr.__dict__)

    def test_json(self):
        fname = data_file('faker_names.json')
        with open(fname, 'rt') as jdat:
            jmsg = self.msgtype.from_json(jdat.read())
        # pmsg = self.msgtype(**self.faker_dict)
        self.assertEqual(jmsg.__dict__, self.msg.__dict__)
        self.assertEqual(repr(jmsg), repr(self.msg))

    def test_json_opts(self):
        dmsg = self.faker_dict.copy()
        dmsg['show_headers'] = True
        dnj = DictAndJson(**dmsg)

        msg = self.msgtype(**dnj.data)
        msg2 = self.msgtype.from_json(dnj.json_string)
        self.assertEqual(msg.__dict__, msg2.__dict__)
        self.assertEqual(msg2.widget_opts['show_headers'], True)
        msg3 = self.msgtype.from_json(dnj.json_string, show_headers=False)
        self.assertEqual(msg3.widget_opts['show_headers'], False)

    def test_text(self):
        fname = data_file('faker_names.text')
        with open(fname, 'rt') as tdat:
            tmsg = self.msgtype.from_text(tdat.read(), col_sep='\t', row_sep='@\n@', mark_header='###')
        self.assertEqual(tmsg.__dict__, self.msg.__dict__)
        self.assertEqual(repr(tmsg), repr(self.msg))


class TestSimple(unittest.TestCase):
    "Test Simple message type"
    @classmethod
    def setUpClass(cls):
        cls.msgtype = message_types.Simple

    def test_choices(self):
        choice = message_types.choices[self.msgtype.__name__]
        self.assertEqual(choice, self.msgtype)

    def test_repr(self):
        msg = self.msgtype(body='abc', summary='some summary', font_size=200)
        msg_from_repr = eval('message_types.' + repr(msg))
        self.assertEqual(msg.__dict__, msg_from_repr.__dict__)


    def test_simple(self):
        stxt = 'summary txt here'
        btxt = 'body txt here'
        msg = self.msgtype(summary=stxt, body=btxt, wow=True)
        self.assertEqual(btxt, msg.body)
        self.assertIn(stxt, msg.summary)
        self.assertEqual({'wow': True}, msg.widget_opts)

    def test_json(self):
        stxt = 'summary txt here'
        btxt = 'body txt here'
        dict_n_json = DictAndJson(summary=stxt, body=btxt, font_size=13)
        msg = self.msgtype(**dict_n_json.data)
        msg2 = self.msgtype.from_json(dict_n_json.json_string)
        self.assertEqual(msg.__dict__, msg2.__dict__)

    def test_json_opts(self):
        dict_n_json = DictAndJson(summary='summ', body='body txt', font_size=12)
        msg = self.msgtype.from_json(dict_n_json.json_string)
        self.assertEqual(msg.widget_opts['font_size'], 12)
        msg = self.msgtype.from_json(dict_n_json.json_string, font_size=14)
        self.assertEqual(msg.widget_opts['font_size'], 14)

    def test_text(self):
        stxt = 'summary txt here'
        btxt = 'body txt is here'
        txt = """{}
        {}
        """.format(stxt, btxt)
        msg = self.msgtype(summary=stxt, body=btxt)
        msg2 = self.msgtype.from_text(txt, row_sep='\n')
        self.assertEqual(msg2.summary, msg.summary)
        self.assertEqual(msg2.body, msg.body)        


    def test_text_opts(self):
        stxt = 'summary txt here'
        btxt = 'body txt is here'
        txt = """{}
        {}
        """.format(stxt, btxt)
        msg = self.msgtype.from_text(txt, row_sep='\n')
        self.assertEqual(msg.widget_opts, {})
        msg = self.msgtype.from_text(txt, row_sep='\n', font_size=30)
        self.assertEqual(msg.widget_opts, {'font_size': 30})


class TestMakeMsg(unittest.TestCase, MsgHelpers):
    @classmethod
    def setUpClass(cls):
        cls.fn = staticmethod(message_types.make_msg)

    def test_simple(self):
        body_txt = 'a b c d'
        summ = 'summary txt'
        msg = self.fn(msg_type='Simple', body=body_txt, font_name='Sans', summary=summ)
        msg2 = message_types.Simple(body=body_txt, font_name='Sans', summary=summ)
        self.assertMsgEqual(msg, msg2)
        msg3 = self.fn(msg_type=message_types.Simple, body=body_txt, font_name='Sans', summary=summ)
        self.assertMsgEqual(msg, msg3)

    def test_table(self):
        body_txt = ['a', 'b', 'c']
        cols = ['Col 1', 'Col 2']
        msg = self.fn(msg_type='Table', body=body_txt, columns=cols, font_size=32)
        msg2 = message_types.Table(body=body_txt, columns=cols, font_size=32)
        self.assertMsgEqual(msg, msg2)
        msg3 = self.fn(msg_type=message_types.Table, body=body_txt, columns=cols, font_size=32)
        self.assertMsgEqual(msg, msg3)
        
        
