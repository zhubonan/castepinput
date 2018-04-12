"""
Module for parsing castep styled inputs
inputs may contain oneline


STANDARDISATION
CASTEP input does not destinguish between low and upper case, but python does.
To stardardise data parsed. Output follows the convension
1. all keys will be in lower case
2. all block names will be in lower case
3. case of the values themselves are not affected
4. content of the blocks are not affected
"""
from __future__ import print_function
from __future__ import division

import os
import re

import numpy as np
import castepinputs.utils as utils

COMMENT_SYMBOLS = ["#", "!"]

block_start = re.compile("%block (\w+)", flags=re.IGNORECASE)
block_finish = re.compile("%endblock (\w+)", flags=re.IGNORECASE)
kw_split = re.compile("[ :=]+")


class FormatError(RuntimeError):
    pass


class BaseParser(object):
    """
    Base parser class
    Does nothing fancy, basic text processing
    """

    def __init__(self, lines):
        """
        Parser for cell/param files for castep.
        May also be useful for OptaDos/CASTEPConv that shares similar
        format.
        Parameters:
        :params lines: A list of the file content or name of a file to be read
        """
        if isinstance(lines, (list, tuple)):
            self._raw_lines = lines  # Raw input lines
        else:
            with open(lines) as fh:
                lin = []
                for line in fh:
                    lin.append(line.strip())
            self._raw_lines = lin

        self._lines = None  # Processed lines
        self._kwlines = None  # key-value paired lines
        self._blocks = None  # A dictionary of blocks

    def parse(self):
        """
        Parser the input file
        """
        self._clean_up_lines()  # Remove comments, blank lines
        self._split_block_kw()  # Extract blocks from the lines
        self._parse_keywords()  # Parse the key, value pair

    @property
    def content(self):
        """A list of lines as inputs for parsing"""
        return self._raw_lines

    @property
    def comments(self):
        if self._comments is None:
            raise RuntimeError("File is not parsed")
        else:
            return self._comments

    def _clean_up_lines(self):
        """
        Filter out comments
        Save cleaned lines in self._lines and
        comments in self._comments
        Make everything not comment in lower case
        """

        lines = self.content
        comments = []
        cleaned_lines = []
        for line in lines:

            if not line:
                continue  # skip empty lines
            line = line.strip()  # Get rid of white spaces

            # We first check for comment
            if line[0] in COMMENT_SYMBOLS:
                comments.append(line[1:].strip())
                continue

            # Check if there is any trailing comments
            for s in COMMENT_SYMBOLS:
                pos = line.find(s)
                if pos != -1:
                    comments.append(line[pos+1:].strip())
                    cld_line = line[:pos].strip()  # Remove trailing space
                    break
                else:
                    cld_line = line
            cleaned_lines.append(cld_line)

        self._lines = cleaned_lines
        self._comments = comments
        return cleaned_lines, comments

    def _split_block_kw(self):
        """
        Split blocks from cleaned_up lines.
        Returns a dictionary of block names and contents
        Save all keyword-value lines in self._kwlines
        """

        if self._lines is None:
            self._clean_up_lines()

        # Extract
        block_indices = {}
        in_block = False
        kwlines = []
        start_name = None
        for i, line in enumerate(self._lines):

            start_match = block_start.match(line)
            if start_match:
                if in_block is True:
                    raise FormatError("End of block {}"
                        " is not detected".format(start_name))
                start = i
                in_block = True
                start_name = start_match.group(1).lower()
                continue

            end_match = block_finish.match(line)
            if end_match:
                finish = i
                end_name = end_match.group(1).lower()
                if in_block is False:
                    raise FormatError("Start of block {} not"
                                      " found".format(end_name))
                elif end_name != start_name:
                    raise FormatError("Mismatch block names, start: {}"
                    " finish: {}".format(start_name, end_name))
                else:
                    block_indices[start_name] = (start, finish)
                    in_block = False
                continue

            if not in_block:
                kwlines.append(line)

        if in_block is True:
            raise FormatError("End of block {}"
                " not detected".format(start_name))

        # Now extract block contents
        blocks = {}
        for key, index in block_indices.items():
            lines = self._lines[index[0]+1:index[1]]
            blocks[key.lower()] = lines

        self._blocks = blocks
        self._kwlines = kwlines
        return blocks, kwlines

    def _parse_keywords(self):
        """Parse keyword, value pairs"""
        out_dict = {}
        for line in self._kwlines:
            s = kw_split.split(line, 1)
            if len(s) == 2:
                key, value = s
            elif len(s) == 1:
                key = s[0]
                value = ""  # Empty string for key without values
            else:
                raise FormatError("Cannot parse line {} into key-value"
                    " pair".format(line))

            out_dict[key.lower()] = value
        self._keywords = out_dict
        return out_dict

    def get_dict(self):
        """
        Get the parsed information in a dictionary
        """
        res = dict(self._keywords)
        res.update(self._blocks)
        return res

class Parser(BaseParser):
    """
    General parser class
    """

    def parse(self):
        """
        Parse the contents
        """
        super(Parser, self).parse()
        old_keywords = self._keywords

        new_keywords = {}
        for key, value in old_keywords.items():
            new_keywords[key] = convert_type_kw(value, key)

        self._keywords = new_keywords



class CellParser(Parser):

    def __init__(self, fname):
        """
        Parser for cell files.
        Parameters
        ----------
        :param fname: Path to the cell file

        Usage
        -----

        parser = CellParser("cellfile.cell")
        parser.parse()
        kws = parser.get_keywords()
        cell = parser.get_cell()
        pos = parser.get_positions()
        """
        super(CellParser, self).__init__(fname)

    def get_cell(self):
        """Return cell vectors"""
        if self._blocks is None:
            self.parse()

        cell = []
        if "lattice_cart" in self._blocks:
            cell_lines = self._blocks['lattice_cart']

            for l in cell_lines:
                cell.append([float(v) for v in l.split()])

        elif "lattice_abc" in self._blocks:
            abc_lines = self._blocks['lattice_abc']

            abc = []
            for l in abc_lines:
                abc.extend([float(v) for v in l.split()])
            assert len(abc) == 6, "Problem in lattice_abc block"

            cell = utils.cell_abcs_to_vec(abc)

        return np.asarray(cell)

    def get_positions(self):
        """
        Positions of ions

        :returns elements: A list of elements
        :returns pos: A list of list of floats of the positions
        :returns tags: A dictionary of tags e.g spin, mixture, label etc
        """
        if self._blocks is None:
            self.parse()

        is_frac = False
        pos_lines = self._blocks.get('positions_abs')
        if not pos_lines:
            pos_lines = self._blocks.get('positions_frac')
            is_frac = True


        if pos_lines:
            pos = []
            elements = []
            for l in pos_lines:
                ls = l.split()
                element = ls[0].capitalize()
                xyz = [float(a) for a in ls[1:4]]
                # Ignore the spin and labels for now
                pos.append(xyz)
                elements.append(element)
        pos = np.array(pos)

        if is_frac:
            # We need to multiple the positions with cells
            cell = self.get_cell()
            pos = np.dot(cell, pos.T).T

        return elements, pos


class ParamParser(CellParser):
    """Parser class for PARAM files"""
    pass

def parse_pos_line(cell_line):
    """
    Parse a line in the cell block.
    Need to treat LABEL, SPIN, MIXTURE properly
    """
    import re
    cell_line = cell_line.strip()
    s = re.split(" ", cell_line, maxsplit=5)
    if len(s) < 4:
        raise ValueError("Cannot understand line: {}".format(cell_line))
    if len(s) == 5:
        tags = s[-1]
    else:
        tags = None

    elem = s[0]
    coor = map(float, s[1:4])

#    if tags is not None:
#        # Parse the tags
#        tags = tags.lower()  # Change to lower case
#        if tags.find("spin=")
    return elem, coor, tags

def convert_type_kw(value, key=None):
    """
    Try to convert type of the value
    """

    try:
        out = int(value)
    except:
        pass
    else:
        return out

    try:
        out = float(value)
    except:
        pass
    else:
        return out

    sline = value.split()
    if len(sline) == 3:
        try:
            out = list(map(int, sline))
        except:
            pass
        else:
            return out

        try:
            out = list(map(float, sline))
        except:
            pass
        else:
            return out

    # If nothing successful
    return out
