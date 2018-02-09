import pytest
from gpopup import utils

def test_0d_str():
    assert utils.message_depth('some message') == 0

def test_0d_int():
    assert utils.message_depth(37) == 0

def test_1d_str():
    x = ['a', 'b', 'c', 'd']
    assert utils.message_depth(x) == 1

def test_1d_int():
    assert utils.message_depth(range(10)) == 1

def test_2d_str():
    x = [('a', 'b'), ('c', 'd')]
    assert utils.message_depth(x) == 2

def test_2d_int():
    x = [(1, 2), (3, 4)]
    assert utils.message_depth(x) == 2

def test_maxdepth_int():
    x = [[[1,],],]
    assert utils.message_depth(x, maxdepth=99) == 3
    assert utils.message_depth(x, maxdepth=2) == 2
    assert utils.message_depth(x, maxdepth=1) == 1

def test_maxdepth_str():
    x = [[['a',],],]
    assert utils.message_depth(x, maxdepth=99) == 3
    assert utils.message_depth(x, maxdepth=2) == 2
    assert utils.message_depth(x, maxdepth=1) == 1

@pytest.fixture
def data4():
    return ('aa', 'bb', 'cc', 'dd')

@pytest.fixture
def data5():
    return ('a', 'b', 'c', 'd', 'e')

def test_data4_take1(data4):
    out = tuple(utils.takeall(1, data4))
    assert out == (('aa',), ('bb',), ('cc',), ('dd',))

def test_data4_take2(data4):
    out = tuple(utils.takeall(2, data4))
    assert out == (('aa', 'bb'), ('cc', 'dd'))

def test_data5_take2(data5):
    out = tuple(utils.takeall(2, data5))
    assert out == (('a', 'b'), ('c', 'd'), ('e',))

def test_data5_take3(data5):
    out = tuple(utils.takeall(3, data5))
    assert out == (('a', 'b', 'c'), ('d', 'e'))

def test_data5_cols1(data5):
    out = utils.vector_to_matrix(data5, ncols=1)
    assert out == (('a',), ('b',), ('c',), ('d',), ('e',))

def test_data5_cols2(data5):
    out = utils.vector_to_matrix(data5, ncols=2)
    assert out == (('a', 'b'), ('c', 'd'), ('e', ''))

def test_data5_cols3(data5):
    out = utils.vector_to_matrix(data5, ncols=3)
    assert out == (('a', 'b', 'c'), ('d', 'e', ''))

@pytest.fixture
def data6():
    return (('a', 'b', 'c'), ('d',))

def test_data(data6):
    out = utils.ensure_row_length(data6, ncols=len(data6[0]))
    assert out == (('a', 'b', 'c'), ('d', '', ''))

def test_fill(data6):
    fill = 'wow'
    out = utils.ensure_row_length(data6, ncols=len(data6[0]), fill=fill)
    assert out == (('a', 'b', 'c'), ('d', fill, fill))

#         self.assertIsInstance(x, utils.FormattedTblMsg)
@pytest.fixture
def data0():
    return 'some message'

@pytest.fixture
def col_tupl():
    return ('Col0', 'Col1', 'Col2')

@pytest.fixture
def data2d():
    return (('a', 'b', 'c'), ('d',))

def test_0d_str(data0):
    mm = utils.format_tbl_msg(data0)
    assert isinstance(mm, utils.FormattedTblMsg)
    assert mm.entries == ((data0,),)
    assert mm.columns == ('',)

def test_0d_str_w_col(data0, col_tupl):
    mm = utils.format_tbl_msg(data0, columns=col_tupl[0:1])
    assert isinstance(mm, utils.FormattedTblMsg)
    assert mm.entries == ((data0,),)
    assert mm.columns == (col_tupl[0],)

def test_0d_str_w_cols(data0, col_tupl):
    mm = utils.format_tbl_msg(data0, columns=col_tupl)
    assert isinstance(mm, utils.FormattedTblMsg)
    assert mm.entries == ((data0, '', ''),)
    assert mm.columns == col_tupl

def test_1d_str(data5):
    mm = utils.format_tbl_msg(data5)
    assert isinstance(mm, utils.FormattedTblMsg)
    assert mm.entries == tuple((x,) for x in data5)
    assert mm.columns == ('',)

def test_1d_str_w_2col(data5):
    mm = utils.format_tbl_msg(data5, columns=2)
    assert isinstance(mm, utils.FormattedTblMsg)
    assert mm.entries == (('a', 'b'), ('c', 'd'), ('e', ''))
    assert mm.columns == ('', '') 

def test_1d_str_w_3col(data5, col_tupl):
    mm = utils.format_tbl_msg(data5, columns=col_tupl)
    assert isinstance(mm, utils.FormattedTblMsg)
    assert mm.entries == (('a', 'b', 'c'), ('d', 'e', ''))
    assert mm.columns == col_tupl

def test_2d_str_w_3col(data2d, col_tupl):
    mm = utils.format_tbl_msg(data2d, columns=col_tupl)
    assert isinstance(mm, utils.FormattedTblMsg)
    assert mm.entries == (('a', 'b', 'c'), ('d', '', ''))
    assert mm.columns == col_tupl
