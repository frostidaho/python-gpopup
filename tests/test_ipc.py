import unittest
from gpopup import ipc

class TestHeader(unittest.TestCase):
    "Test packing and unpacking message headers"
    def test_pack_unpack(self):
        header = ('json', 301)
        header_bytes = ipc._pack_header(*header)
        header_out = ipc._unpack_header(header_bytes)
        self.assertEqual(header, header_out)
        self.assertEqual(header[0], header_out.type)
        self.assertEqual(header[1], header_out.length)
