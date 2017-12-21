"""
Test parser
"""


import os
import unittest
from castepinputs.parser import BaseParser, CellParser

current_path = os.path.split(__file__)[0]

class TestParser(unittest.TestCase):

    def get_cellfile(self, index=None):

        if index is not None:
            fn = "cell_example_{}.cell".format(index)
        else:
            fn = "cell_example.cell"

        return os.path.join(current_path, 'data/' + fn)

    def setUp(self):
        self.parser = BaseParser(os.path.join(current_path, 'data/cell_example.cell'))

    def test_read(self):
        self.assertTrue(self.parser.content)

    def test_clean_up_lines(self):
        self.parser._clean_up_lines()
        lines, comments = self.parser._clean_up_lines()
        self.assertEqual(len(comments), 4)
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

    def test_cell_parser(self):
        cell_parser = CellParser(self.get_cellfile())
        cell_parser.parse()
        print(cell_parser.get_blocks())
        cell = cell_parser.get_cell()
        self.assertEqual(len(cell), 3)

    def test_cell_parser2(self):
        cell_parser = CellParser(self.get_cellfile(2))
        cell_parser.parse()
        print(cell_parser.get_blocks())
        cell = cell_parser.get_cell()
        self.assertEqual(len(cell), 3)


if __name__ == "__main__":
    unittest.main()
