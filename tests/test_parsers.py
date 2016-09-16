import unittest
import json

from gpopup import message_parsers
from gpopup import utils


class TestHtml(unittest.TestCase):
    "Test Html parser"
    @classmethod
    def setUpClass(cls):
        cls.fn = staticmethod(message_parsers.html_to_2d_tuple)

    def test_data_w_headers(self):
        data_w_headers = """\
        <table style="width:100%">
        <tr>
        <th>Firstname ok</th>
        <th>Lastname</th> 
        <th>Age</th>
        </tr>
        <tr>
        <td>Jill</td>
        <td>Smith</td> 
        <td>50</td>
        </tr>
        <tr>
        <td>Eve</td>
        <td>Jackson</td> 
        <td>94</td>
        </tr>
        </table>
        """

        res_w_headers = utils.FormattedTblMsg(
            entries=(('Jill', 'Smith', '50'), ('Eve', 'Jackson', '94')),
            columns=('Firstname ok', 'Lastname', 'Age')
        )
        self.assertEqual(self.fn(data_w_headers), res_w_headers)

    def test_data_no_header(self):
        data_w_headers = """\
        <table style="width:100%">
        <tr>
        <td>Firstname ok</td>
        <td>Lastname</td> 
        <td>Age</td>
        </tr>
        <tr>
        <td>Jill</td>
        <td>Smith</td> 
        <td>50</td>
        </tr>
        <tr>
        <td>Eve</td>
        <td>Jackson</td> 
        <td>94</td>
        </tr>
        </table>
        """

        res_w_headers = utils.FormattedTblMsg(
            entries=(
                ('Firstname ok', 'Lastname', 'Age'),
                ('Jill', 'Smith', '50'),
                ('Eve', 'Jackson', '94'),
            ),
            columns=('', '', '')
        )
        self.assertEqual(self.fn(data_w_headers), res_w_headers)



class TestJson(unittest.TestCase):
    "Test JSON message parser"
    @classmethod
    def setUpClass(cls):
        from string import ascii_letters
        tot = []
        row = []
        for i,c in enumerate(ascii_letters):
            if (i % 4 == 0) and (i > 0):
                tot.append(row)
                row = []
            row.append(c)

        cls.raw_fn = staticmethod(utils.format_tbl_msg)
        cls.fn = staticmethod(message_parsers.json_to_2d_tuple)
        cls.data0 = {'message': tot, 'columns': len(tot[0])*['']}
        cls.res0 = utils.format_tbl_msg(**cls.data0)
        cls.json0 = json.dumps(cls.data0)


        cls.data1 = {'message': tot, 'columns': ['Col {}'.format(i)
                                                 for i in range(len(tot[0]))]}
        cls.res1 = utils.format_tbl_msg(**cls.data1)
        cls.json1 = json.dumps(cls.data1)

    def test_proper_dict(self):
        "test a json dictionary with message and columns entries"
        self.assertEqual(self.fn(self.json0), self.res0)

    def test_incomplete_dict(self):
        dat = self.data0.copy()
        dat.pop('columns')
        json_dat = json.dumps(dat)
        self.assertEqual(self.fn(json_dat), self.raw_fn(**dat))

    def test_dict_with_headers(self):
        self.assertEqual(self.fn(self.json1), self.res1)

    def test_json_msg_array(self):
        msg = self.data0['message']
        json_msg = json.dumps(msg)
        self.assertEqual(self.fn(json_msg), self.raw_fn(msg))



class TestText(unittest.TestCase):
    "Test text message parser"
    @classmethod
    def setUpClass(cls):
        from string import ascii_letters
        tot = []
        row = []
        for i,c in enumerate(ascii_letters):
            if (i % 4 == 0) and (i > 0):
                tot.append(row)
                row = []
            row.append(c)

        cls.raw_fn = staticmethod(utils.format_tbl_msg)
        cls.fn = staticmethod(message_parsers.text_to_2d_tuple)

    def test_basic(self):
        txt = """\
        1	2	3
        4	5	6
        """
        res = self.fn(txt, col_sep='\t', row_sep='\n')
        res_known = self.raw_fn([['1', '2', '3'], ['4', '5', '6']])
        self.assertEqual(res, res_known)


    def test_basic_w_header(self):
        txt = """\
        1	2	3
        4	5	6
        Col1	Col2	Col3 ###
        """
        res = self.fn(txt, col_sep='\t', row_sep='\n', mark_header='###')
        res_known = self.raw_fn([['1', '2', '3'], ['4', '5', '6']],
                                columns=['Col1', 'Col2', 'Col3'])
        self.assertEqual(res, res_known)


    def test_other_separators(self):
        txt = """\
        1@@2@@
        3!!4	@@ 5 @@ 6!!
        ### Col1 @@ Col2 @@ Col3
        """
        res = self.fn(txt, col_sep='@@', row_sep='!!', mark_header='###')
        res_known = self.raw_fn([['1', '2', '3'], ['4', '5', '6']],
                                columns=['Col1', 'Col2', 'Col3'])
        self.assertEqual(res, res_known)
