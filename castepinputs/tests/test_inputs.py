"""
Test module for the inputs
"""
import os
from castepinputs.inputs import CastepInput, CellInput
from castepinputs.inputs import Block, parse_pos_line, construct_pos_line
import pytest
import numpy as np


current_path = os.path.split(__file__)[0]
@pytest.fixture
def basic_input():
    c = CastepInput()
    c["a"] = "a"
    c["b"] = Block(["a", "b"])
    c["c"] = 5
    return c


@pytest.fixture
def cell_input():
    c = CellInput()
    c["symmetry_generate"] = True
    return c

def test_input_gen(basic_input):
    """
    Test basic function of generate inputs
    """
    lines = basic_input.get_file_lines()
    assert lines[0].split(":")[0].strip() == "a"
    assert lines[0].split(":")[1].strip() == "a"
    assert lines[1].startswith("%")
    assert lines[4].startswith("%")


def test_header(basic_input):
    """
    Test adding header
    """
    basic_input.header = ["Hello World"]
    lines = basic_input.get_file_lines()
    assert lines[0] == "# Hello World"

    basic_input.header = ["#Hello World"]
    lines = basic_input.get_file_lines()
    assert lines[0] == "#Hello World"


def test_unit(basic_input):
    """
    Test the unit system
    """
    basic_input.units["a"] = "eV"
    basic_input.units["b"] = "eV"
    lines = basic_input.get_file_lines()
    assert lines[0].split(":")[1].strip()[-2:] == "eV"
    assert lines[2].strip() == "eV"


def test_string(basic_input):
    lines = basic_input.get_file_lines()
    "\n".join(lines) == basic_input.get_string()


def test_save(basic_input, tmpdir):
    outname = str(tmpdir.join("test.in"))
    basic_input.save(outname)
    os.remove(outname)


def test_read_save(basic_input, tmpdir):
    outname = str(tmpdir.join("test.in"))
    basic_input.save(outname)
    input2 = CastepInput()
    input2.load_file(outname)
    assert dict(input2) == dict(basic_input)


# Tests for CellInputs
def test_pos_lines():
    """
    Rest construction and presing of positions lines
    """

    l = "Ce 1.23 2.34 2.6 SPIN=1 LABEL=Ce1 MIX=(1 1)"
    elem, pos, tags = parse_pos_line(l)
    assert elem == "Ce"
    assert pos == [1.23, 2.34, 2.6]
    assert tags == "SPIN=1 LABEL=Ce1 MIX=(1 1)"
    lines = construct_pos_line(elem, pos, tags)
    r = parse_pos_line(lines)
    for a in zip(r, [elem, pos, tags]):
        assert a[0] == a[1]

def test_input_pos_lines(cell_input):
    """
    Rest construction and presing of positions lines
    """
    l = "Ce 1.23 2.34 2.6 SPIN=1 LABEL=Ce1 MIX=(1 1)"
    cell_input["positions_abs"] = Block([l] * 3)
    elem, pos, tags = cell_input.get_positions()
    assert elem == ["Ce"] * 3
    assert np.all(pos == np.array([[1.23, 2.34, 2.6]] * 3))
    assert tags == ["SPIN=1 LABEL=Ce1 MIX=(1 1)"] * 3
    cell_input.set_positions(elem, pos, tags)

    nelem, npos, ntags = cell_input.get_positions()
    assert nelem == elem
    assert np.all(npos == pos)
    assert ntags == tags


def test_set_cell(cell_input):

    cin = [[1., 0, 0], [0, 1.5, 0], [0, 0, 1.]]
    cell_input.set_cell(cin)
    assert np.all(cell_input.get_cell() == cin)

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
    cin = CellInput.from_file(
        os.path.join(current_path, 'data/cell_example_{}.cell'.format(data)))
    assert cin.get_cell().tolist() == expected["cell"]
    assert cin.get_positions()[1].tolist() == expected["pos"]