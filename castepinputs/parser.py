"""
Module for parsing input files
"""

import os
import re


COMMENT_SYMBOLS = ["#", "!"]

block_start = re.compile("%block (\w+)", flags=re.IGNORECASE)
block_finish = re.compile("%endblock (\w+)", flags=re.IGNORECASE)
kw_split = re.compile("[ :=]+")


class FormatError(RuntimeError):
    pass


class BaseParser:

    def __init__(self, fname):
        """Initialise an instance of the parser"""
        self.fname = fname
        self._lines = None
        self._content = None
        self._kwlines = None
        self._blocks = None

    def parse(self):
        """
        Parser the input file
        """
        self._clean_up_lines()  # Remove comments, blank lines
        self._split_block_kw()  # Extract blocks from the lines
        self._parse_keywords()  # Parse the key, value pair


    @property
    def content(self):
        """Return raw string of the input file"""
        if self._content is None:
            with open(self.fname) as fp:
                self._content = fp.read()
        return self._content

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

        lines = self.content.split("\n")
        comments = []
        cleaned_lines = []
        for line in lines:

            if not line:
                continue  # skip empty lines
            line = line.strip()  # Get rid of white spaces

            # We first check for comment
            if line[0] in COMMENT_SYMBOLS:
                comments.append(line[1:])
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
            cleaned_lines.append(cld_line.lower())

        self._lines = cleaned_lines
        self._comments = comments
        return cleaned_lines, comments

    def _split_block_kw(self):
        """
        Extract blocks
        Returns a dictionary of block names and contents
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
                    "finish: {}".format(start_name, end_name))
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
                value = None
            else:
                raise FormatError("Cannot parse line {} into key-value"
                    " pair".format(line))

            out_dict[key.lower()] = value
        self._keywords = out_dict
        return out_dict

    def get_keywords(self):
        """Return the keywords as a dictionary"""
        return self._keywords

    def get_blocks(self):
        """Returns the blocks as a dictionary"""
        return self._blocks

class CellParser(BaseParser):


    def get_cell(self):
        """Return cell vectors"""
        if self._blocks is None:
            self.parse()
        cell_lines = self._blocks['lattice_cart']

        cell = []
        for l in cell_lines:
            cell.append(int(v) for v in l.split())
        return cell

    def get_positions(self):
        """
        Positions of ions

        :returns elements: A list of elements
        :returns pos: A list of list of floats of the positions
        :returns tags: A dictionary of tags e.g spin, mixture, label etc
        """
        if self._blocks is None:
            self.parse()
        pos_lines = self._blocks['positions_abs']

        pos = []
        elements = []
        for l in pos_lines:
            ls = l.split()
            element = ls[0]
            xyz = [float(a) for a in ls[1:4]]
            # Ignore the spin and labels for now
            pos.append(xyz)
            elements.append(element)
        return elements, pos



class ParamParser(BaseParser):

    def _split_block_kw(self):
        self._kwlines = self._lines
