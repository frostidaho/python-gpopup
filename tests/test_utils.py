import unittest
from gpopup import utils

class TestMsgDepth(unittest.TestCase):
    "Test utils.message_depth"
    @classmethod
    def setUpClass(cls):
        cls.fn = staticmethod(utils.message_depth)

    def test_0d_str(self):
        self.assertEqual(self.fn('some message'), 0)

    def test_0d_int(self):
        self.assertEqual(self.fn(37), 0)

    def test_1d_str(self):
        x = ['a', 'b', 'c', 'd']
        self.assertEqual(self.fn(x), 1)

    def test_1d_int(self):
        self.assertEqual(self.fn(range(10)), 1)

    def test_2d_str(self):
        x = [('a', 'b'), ('c', 'd')]
        self.assertEqual(self.fn(x), 2)

    def test_2d_int(self):
        x = [(1, 2), (3, 4)]
        self.assertEqual(self.fn(x), 2)

    def test_maxdepth_int(self):
        x = [[[1,],],]
        self.assertEqual(self.fn(x, maxdepth=99), 3)
        self.assertEqual(self.fn(x, maxdepth=2), 2)
        self.assertEqual(self.fn(x, maxdepth=1), 1)

    def test_maxdepth_str(self):
        x = [[['a',],],]
        self.assertEqual(self.fn(x, maxdepth=99), 3)
        self.assertEqual(self.fn(x, maxdepth=2), 2)
        self.assertEqual(self.fn(x, maxdepth=1), 1)



class TestTakeAll(unittest.TestCase):
    "Test utils.takeall"
    @classmethod
    def setUpClass(cls):
        cls.fn = staticmethod(utils.takeall)
        cls.data4 = ('aa', 'bb', 'cc', 'dd')
        cls.data5 = ('a', 'b', 'c', 'd', 'e')

    def test_data4_take1(self):
        out = tuple(self.fn(1, self.data4))
        self.assertEqual(out, (('aa',), ('bb',), ('cc',), ('dd',)))

    def test_data4_take2(self):
        out = tuple(self.fn(2, self.data4))
        self.assertEqual(out, (('aa', 'bb'), ('cc', 'dd')))

    def test_data5_take2(self):
        out = tuple(self.fn(2, self.data5))
        self.assertEqual(out, (('a', 'b'), ('c', 'd'), ('e',)))

    def test_data5_take3(self):
        out = tuple(self.fn(3, self.data5))
        self.assertEqual(out, (('a', 'b', 'c'), ('d', 'e')))


class TestVectorToMatrix(unittest.TestCase):
    "Test utils.vector_to_matrix"
    @classmethod
    def setUpClass(cls):
        cls.fn = staticmethod(utils.vector_to_matrix)
        cls.data5 = ('a', 'b', 'c', 'd', 'e')

    def test_data5_cols1(self):
        out = self.fn(self.data5, ncols=1)
        self.assertEqual(out, (('a',), ('b',), ('c',), ('d',), ('e',)))

    def test_data5_cols2(self):
        out = self.fn(self.data5, ncols=2)
        self.assertEqual(out, (('a', 'b'), ('c', 'd'), ('e', '')))

    def test_data5_cols3(self):
        out = self.fn(self.data5, ncols=3)
        self.assertEqual(out, (('a', 'b', 'c'), ('d', 'e', '')))


class TestEnsureRowLength(unittest.TestCase):
    "Test utils.vector_to_matrix"
    @classmethod
    def setUpClass(cls):
        cls.fn = staticmethod(utils.ensure_row_length)
        cls.data = (('a', 'b', 'c'), ('d',))

    def test_data(self):
        out = self.fn(self.data, ncols=len(self.data[0]))
        self.assertEqual(out, (('a', 'b', 'c'), ('d', '', '')))

    def test_fill(self):
        fill = 'wow'
        out = self.fn(self.data, ncols=len(self.data[0]), fill=fill)
        self.assertEqual(out, (('a', 'b', 'c'), ('d', fill, fill)))

class TestMsg2Matrix(unittest.TestCase):
    "Test utils.format_msg"
    def assertIsFormattedMsg(self, x):
        self.assertIsInstance(x, utils.FormattedMsg)

    def assertEntriesEqual(self, msgmatrix, y):
        self.assertEqual(msgmatrix.entries, y)

    def assertColsEqual(self, msgmatrix, y):
        self.assertEqual(msgmatrix.columns, y)

    @classmethod
    def setUpClass(cls):
        cls.fn = staticmethod(utils.format_msg)
        cls.data0 = 'some message'
        cls.col_tupl = ('Col0', 'Col1', 'Col2')
        cls.data5 = ('a', 'b', 'c', 'd', 'e')
        cls.data2d = (('a', 'b', 'c'), ('d',))

    def test_0d_str(self):
        mm = self.fn(self.data0)
        self.assertIsFormattedMsg(mm)
        self.assertEntriesEqual(mm, ((self.data0,),))
        self.assertColsEqual(mm, ('',))

    def test_0d_str_w_col(self):
        mm = self.fn(self.data0, columns=self.col_tupl[0:1])
        self.assertIsFormattedMsg(mm)
        self.assertEntriesEqual(mm, ((self.data0,),))
        self.assertColsEqual(mm, (self.col_tupl[0],))

    def test_0d_str_w_cols(self):
        mm = self.fn(self.data0, columns=self.col_tupl)
        self.assertIsFormattedMsg(mm)
        self.assertEntriesEqual(mm, ((self.data0, '', ''),))
        self.assertColsEqual(mm, self.col_tupl)

    def test_1d_str(self):
        mm = self.fn(self.data5)
        self.assertIsFormattedMsg(mm)
        self.assertEntriesEqual(mm, tuple((x,) for x in self.data5))
        self.assertColsEqual(mm, ('',))

    def test_1d_str_w_2col(self):
        mm = self.fn(self.data5, columns=2)
        self.assertIsFormattedMsg(mm)
        self.assertEntriesEqual(mm, (('a', 'b'), ('c', 'd'), ('e', '')))
        self.assertColsEqual(mm, ('', ''))

    def test_1d_str_w_3col(self):
        mm = self.fn(self.data5, columns=self.col_tupl)
        self.assertIsFormattedMsg(mm)
        self.assertEntriesEqual(mm, (('a', 'b', 'c'), ('d', 'e', '')))
        self.assertColsEqual(mm, self.col_tupl)

    def test_2d_str_w_3col(self):
        mm = self.fn(self.data2d, columns=self.col_tupl)
        self.assertIsFormattedMsg(mm)
        self.assertEntriesEqual(mm, (('a', 'b', 'c'), ('d', '', '')))
        self.assertColsEqual(mm, self.col_tupl)
        

