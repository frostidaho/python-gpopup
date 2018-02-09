import pytest


class DictAndJson(object):
    def __init__(self, **kwargs):
        self.data = kwargs

    @property
    def json_string(self):
        from json import dumps
        return dumps(self.data)

def data_file(name):
    from os import path
    tests_dir = path.dirname(path.realpath(__file__))
    return path.join(tests_dir, 'data', name)

def msg_equal(msg1, msg2):
    assert msg1.__dict__ == msg2.__dict__
    assert msg1.as_dict == msg2.as_dict
    assert repr(msg1) == repr(msg2)
    return True

@pytest.fixture(scope='function')
def faker_dict():
    with open(data_file('faker_names.python'), 'rt') as faker_names:
        faker_dict = eval(faker_names.read())
    return faker_dict

@pytest.fixture
def faker_dict_msg(faker_dict, message_types):
    return message_types.Table(**faker_dict)
    
def test_choices(message_types):
    for choice in message_types.choices.keys():
        assert message_types.choices[choice].__name__ == choice

def test_table_repr(message_types):
    Table = message_types.choices['Table']
    msg = Table(body=['a', 'b', 'c'], columns=['Col 1', 'Col 2'], font_size=13)
    msg_from_repr = eval('message_types.' + repr(msg))
    assert msg_equal(msg, msg_from_repr)

def test_table_json(message_types, faker_dict_msg):
    fname = data_file('faker_names.json')
    with open(fname, 'rt') as jdat:
        jmsg = message_types.Table.from_json(jdat.read())
    assert msg_equal(jmsg, faker_dict_msg)

def test_table_json_opts(message_types, faker_dict):
    faker_dict['show_headers'] = True
    dnj = DictAndJson(**faker_dict)
    Table = message_types.Table

    msg = Table(**dnj.data)
    msg2 = Table.from_json(dnj.json_string)
    assert msg_equal(msg, msg2)
    assert msg2.widget_opts['show_headers'] is True
    msg3 = Table.from_json(dnj.json_string, show_headers=False)
    assert msg3.widget_opts['show_headers'] is False

def test_table_text(message_types, faker_dict_msg):
    fname = data_file('faker_names.text')
    Table = message_types.Table
    with open(fname, 'rt') as tdat:
        tmsg = Table.from_text(tdat.read(), col_sep='\t', row_sep='@\n@', mark_header='###')
    assert msg_equal(tmsg, faker_dict_msg)

def test_simple_repr(message_types):
    msg = message_types.Simple(body='abc', summary='some summary', font_size=200)
    msg_from_repr = eval('message_types.' + repr(msg))
    assert msg_equal(msg, msg_from_repr)

def test_simple(message_types):
    stxt = 'summary txt here'
    btxt = 'body txt here'
    msg = message_types.Simple(summary=stxt, body=btxt, wow=True)
    assert btxt == msg.body
    assert stxt in msg.summary
    assert {'wow': True} == msg.widget_opts

def test_simple_json(message_types):
    stxt = 'summary txt here'
    btxt = 'body txt here'
    dict_n_json = DictAndJson(summary=stxt, body=btxt, font_size=13)
    msg = message_types.Simple(**dict_n_json.data)
    msg2 = message_types.Simple.from_json(dict_n_json.json_string)
    assert msg_equal(msg, msg2)

def test_simple_json_opts(message_types):
    dict_n_json = DictAndJson(summary='summ', body='body txt', font_size=12)
    msg = message_types.Simple.from_json(dict_n_json.json_string)
    assert msg.widget_opts['font_size'] == 12
    msg = message_types.Simple.from_json(dict_n_json.json_string, font_size=14)
    assert msg.widget_opts['font_size'] == 14

def test_simple_text(message_types):
    stxt = 'summary txt here'
    btxt = 'body txt is here'
    txt = """{}
    {}
    """.format(stxt, btxt)
    msg = message_types.Simple(summary=stxt, body=btxt)
    msg2 = message_types.Simple.from_text(txt, row_sep='\n')
    assert msg_equal(msg2, msg)
    assert msg2.summary == msg.summary
    assert msg2.body == msg.body

def test_simple_text_opts(message_types):
    stxt = 'summary txt here'
    btxt = 'body txt is here'
    txt = """{}
    {}
    """.format(stxt, btxt)
    msg = message_types.Simple.from_text(txt, row_sep='\n')
    assert msg.widget_opts == {}
    msg = message_types.Simple.from_text(txt, row_sep='\n', font_size=30)
    assert msg.widget_opts == {'font_size': 30}

def test_make_msg_simple(message_types):
    body_txt = 'a b c d'
    summ = 'summary txt'
    msg = message_types.make_msg(msg_type='Simple', body=body_txt, font_name='Sans', summary=summ)
    msg2 = message_types.Simple(body=body_txt, font_name='Sans', summary=summ)
    assert msg_equal(msg, msg2)
    msg3 = message_types.make_msg(msg_type=message_types.Simple, body=body_txt, font_name='Sans', summary=summ)
    assert msg_equal(msg, msg3)

def test_make_msg_table(message_types):
    body_txt = ['a', 'b', 'c']
    cols = ['Col 1', 'Col 2']
    msg = message_types.make_msg(msg_type='Table', body=body_txt, columns=cols, font_size=32)
    msg2 = message_types.Table(body=body_txt, columns=cols, font_size=32)
    assert msg_equal(msg, msg2)
    msg3 = message_types.make_msg(msg_type=message_types.Table, body=body_txt, columns=cols, font_size=32)
    assert msg_equal(msg, msg3)
