"""
Classes for .param and .cell files
"""
from __future__ import absolute_import
from collections import OrderedDict
import numpy as np
from .parser import Parser, PlainParser
from .common import Block, cell_abcs_to_vec
from six.moves import map
from six.moves import zip



class CastepInput(OrderedDict):
    """
    Class for storing key - values pairs of CASTEP inputs
    This class can be used for .param, .cell and also other CASTEP style
    inputs such as OptaDos's odi file

    ``self.get_file_lines`` is used for getting a list of strings as
    lines to be written to the file

    ``self.get_string`` is used for getting the content to be passed
    to ``write`` function of a file-like object

    sepecial properties:
    * ``header`` a list of lines to be put into the header
    * ``units`` a dictionary of the units
    """
    def __init__(self, *args, **kwargs):
        super(CastepInput, self).__init__(*args, **kwargs)
        self.header = []
        self.units = {}

    def get_file_lines(self):
        """
        Return a list of strings to be write out to the files
        """
        lines = []
        for h in self.header:
            if not h.startswith("#"):
                lines.append("# " + h)
            else:
                lines.append(h)

        for key, value in self.items():
            if isinstance(value, Block):
                lines.append("%BLOCK {}".format(key))
                if key in self.units:
                    lines.append("{}".format(self.units[key]))
                for v in value:
                    lines.append(v)
                lines.append("%ENDBLOCK {}".format(key))
            else:
                # If a list/tuple is passed join into a string
                if isinstance(value, (tuple, list)):
                    value = " ".join(map(str, value))
                if value:
                    l = "{:<20}: {}".format(key, value)
                else:
                    l = key
                if key in self.units:
                    l = l + " " + self.units[key]
                lines.append(l)

        return lines

    def get_string(self):
        return "\n".join(self.get_file_lines())

    def save(self, fh):
        with open(fh, "w") as fh:
            fh.write(self.get_string())

    @classmethod
    def from_file(cls, fn, plain=False):
        """
        Constrant an instance from the file
        """
        out = cls()
        out.load_file(fn, plain)
        return out

    def load_file(self, fn, plain=False):
        """
        Load from the file
        """
        with open(fn) as fh:
            lines = fh.readlines()
        if plain:
            p = PlainParser(lines)
        else:
            p = Parser(lines)
        dict_out = p.get_dict()
        for k, value in dict_out.items():
            self.__setitem__(k, value)

    def test_read_write(self, basic_input):
        """
        Adhoc test of readin and writing
        """
        import tempfile
        import os
        outname = os.path.join(tempfile.mkdtemp(), "test.in")
        self.save(outname)
        input2 = type(self)()
        input2.load_file(outname)
        assert dict(input2) == dict(basic_input)


class ParamInput(CastepInput):
    pass


class CellInput(CastepInput):

    def get_cell(self):
        """Return cell vectors"""

        cell = []
        if "lattice_cart" in self:
            cell_lines = self['lattice_cart']

            for l in cell_lines:
                cell.append([float(v) for v in l.split()])

        elif "lattice_abc" in self:
            abc_lines = self['lattice_abc']

            abc = []
            for l in abc_lines:
                abc.extend([float(v) for v in l.split()])
            assert len(abc) == 6, "Problem in lattice_abc block"

            cell = cell_abcs_to_vec(abc)

        return np.asarray(cell)

    def get_positions(self):
        """
        Positions of ions

        :returns elements: A list of elements
        :returns pos: A list of list of floats of the positions
        :returns tags: A dictionary of tags e.g spin, mixture, label etc
        """
        is_frac = False
        pos_lines = self.get('positions_abs')
        if not pos_lines:
            pos_lines = self.get('positions_frac')
            is_frac = True
        if not pos_lines:
            raise RuntimeError("No positions defined")


        elems = []
        pos = []
        tags = []
        for l in pos_lines:
            e, p, t = parse_pos_line(l)
            elems.append(e)
            pos.append(p)
            tags.append(t)

        pos = np.array(pos)

        if is_frac:
            # We need to multiple the positions with cells
            cell = self.get_cell()
            pos = np.dot(cell, pos.T).T

        return elems, pos, tags


    def set_cell(self, cell):
        """
        Set cell. Accept a length 3 list/array or 3x3 list/array.
        """
        cell_lines = Block()
        cell = np.asarray(cell)
        if cell.shape == (3,):
            cell = np.diag(cell)
        if cell.shape != (3, 3):
            raise ValueError("Cell must be a 3x3 matrix. But {} is given".format(cell))

        for x in cell:
            cell_lines.append("{:.10f}  {:.10f}  {:.10f}".format(*x))

        self.__setitem__("lattice_cart", Block(cell_lines))


    def set_positions(self, elements, positions, tags=None, frac=False):
        """
        Set positions
        """
        if frac:
            bname = "positions_frac"
        else:
            bname = "positions_abs"

        pos_lines = Block()
        if not tags:
            tags = [""] * len(elements)
        for e, p, t in zip(elements, positions, tags):
            pos_lines.append(construct_pos_line(e, p, t))

        self.__setitem__(bname, Block(pos_lines))


def parse_pos_line(cell_line):
    """
    Parse single line in the cell block.
    Return element, coorindates and a dictionary of tags
    """

    import re
    cell_line = cell_line.strip()
    s = re.split(r"[\s]+", cell_line, maxsplit=4)
    if len(s) < 4:
        raise ValueError("Cannot understand line: {}".format(cell_line))
    if len(s) == 5:
        tags = s[-1]
    else:
        tags = ""

    elem = s[0].capitalize()
    coor = list(map(float, s[1:4]))

    return elem, coor, tags


def construct_pos_line(elem, coor, tags):
    """
    Do the opposite of the parse_pos_line
    """
    line = "{elem}  {x:.10f} {y:.10f} {z:.10f} {tags}"

    return line.format(elem=elem, x=coor[0], y=coor[1], z=coor[2],
                       tags=tags)

