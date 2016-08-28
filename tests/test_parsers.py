import unittest
from gpopup import message_parsers
from gpopup import utils


class TestHtml(unittest.TestCase):
    "Test utils.message_depth"
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

        res_w_headers = utils.FormattedMsg(
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

        res_w_headers = utils.FormattedMsg(
            entries=(
                ('Firstname ok', 'Lastname', 'Age'),
                ('Jill', 'Smith', '50'),
                ('Eve', 'Jackson', '94'),
            ),
            columns=('', '', '')
        )
        self.assertEqual(self.fn(data_w_headers), res_w_headers)

