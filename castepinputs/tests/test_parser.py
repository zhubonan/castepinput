"""
Test parser
"""


import os
import unittest
from castepinputs.parser import BaseParser

current_path = os.path.split(__file__)[0]

class TestParser(unittest.TestCase):

    def setUp(self):
        self.parser = BaseParser(os.path.join(current_path, 'data/cell_example.cell'))

    def test_read(self):
        self.assertTrue(self.parser.content)

    def test_clean_up_lines(self):
        self.parser._clean_up_lines()
        lines, comments = self.parser._clean_up_lines()
        self.assertEqual(len(lines), 6)
        self.assertEqual(len(comments), 3)
        #print(lines, comments)

    def test_split_blocks(self):
        self.parser._clean_up_lines()
        block, kws = self.parser._split_block_kw()
        #print(block, kws)

    def test_kw_parse(self):
        self.parser._clean_up_lines()
        self.parser._split_block_kw()
        out = self.parser._parse_keywords()
        self.assertEqual(out['kpoints_mp_grid'], '1 1 1')
        self.assertEqual(out['kpoint_mp_grid'], '2 2 2')
