"""
Test parser
"""

import os
import pytest
from castepinputs.parser import BaseParser, CellParser
from castepinputs.parser import Block

current_path = os.path.split(__file__)[0]

lines_example = [
    "fix_all_cell:True", "kpoints_mp_grid=4 4 4 # Foo",
    "cut_off_Energy 300   #Bar", "xc_functional :  pbesol", "SYMMETRY_GENERATE"
]

expected_lines = [
    "fix_all_cell:True", "kpoints_mp_grid=4 4 4", "cut_off_Energy 300",
    "xc_functional :  pbesol", "SYMMETRY_GENERATE"
]

expected_comments = ["Foo", "Bar"]

block_lines = ["%BLOCK SPECIES_POT", "O C9", "%ENDBLOCK SPECIES_POT"]

expected_kw_dict = {
    "fix_all_cell": "True",
    "kpoints_mp_grid": "4 4 4",
    "cut_off_energy": "300",
    "xc_functional": "pbesol",
    "symmetry_generate": ""
}
expected_block_dict = {"species_pot": Block(["O C9"])}


@pytest.fixture
def base_parser():
    return BaseParser(lines_example)


@pytest.fixture
def cell_parser():
    return CellParser(os.path.join(current_path, 'data/cell_example_1.cell'))


def testBase_clean_up(base_parser):
    """
    Test cleaning up of the lines
    """
    lines, comments = base_parser._clean_up_lines()
    assert lines == expected_lines
    assert comments == expected_comments


def testBase_blocks(base_parser):
    """
    Test parsing the blocks
    """
    base_parser._raw_lines += block_lines
    base_parser._clean_up_lines()
    blocks, kwlines = base_parser._split_block_kw()
    assert "species_pot" in blocks
    assert kwlines == expected_lines
    assert base_parser._blocks == expected_block_dict


def testBase_outputs(base_parser):
    """
    Test parsing keyword value pairs and final output
    """
    base_parser._raw_lines += block_lines
    base_parser.parse()
    assert base_parser._keywords == expected_kw_dict

    res_dict = expected_kw_dict.copy()
    res_dict.update(expected_block_dict)
    assert base_parser.get_plain_dict() == res_dict


def test_cell_parser(cell_parser):
    cell_parser.parse()
    cell = cell_parser.get_cell()
    assert len(cell), 3

    out_dict = cell_parser.get_plain_dict()
    assert out_dict["kpoints_mp_grid"] == [1, 1, 1]
    assert out_dict["kpoint_mp_grid"] == [2, 2, 2]
    assert "COMMENT1" in cell_parser.comments


@pytest.mark.parametrize("data, expected",
                         [[
                             1,
                             {
                                 "pos": [[1, 1, 1], [2, 2, 2]],
                                 "cell": [[4, 0, 0], [0, 4, 0], [0, 0, 4]]
                             }
                         ],
                          [
                              2,
                              {
                                  "pos": [[0, 0, 0], [1, 1, 1]],
                                  "cell": [[2, 0, 0], [0, 2, 0], [0, 0, 2]]
                              }
                          ]])
def test_cell_parser_cell_and_pos(data, expected):
    parser = CellParser(
        os.path.join(current_path, 'data/cell_example_{}.cell'.format(data)))
    parser.parse()
    assert parser.get_cell().tolist() == expected["cell"]
    assert parser.get_positions()[1].tolist() == expected["pos"]
