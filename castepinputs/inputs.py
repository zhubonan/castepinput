"""
Classes for .param and .cell files
"""
from collections import OrderedDict
from .parser import ParamParser, CellParser, Parser
from .utils import Block


class CastepInput(OrderedDict, Parser):
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
            elif isinstance(value, (tuple, list)):
                raise RuntimeError("List is not allowed. Please use Block type")
            else:
                l = "{:<20}: {}".format(key, value)
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
    def from_file(cls, fn):
        """
        Constrant an instance from the file
        """
        out = cls()
        out.load_file(fn)
        return out

    def load_file(self, fn):
        """
        Load from the file
        """
        with open(fn) as fh:
            lines = fh.readlines()
        super(CastepInput, self)._init(lines)
        dict_out = self.get_dict()
        for k, value in dict_out.items():
            self.__setitem__(k, value)

    def test_read_write(self, basic_input):
        """
        Adhoc test of reading and writing
        """
        import tempfile
        import os
        outname = os.path.join(tempfile.mkdtemp(), "test.in")
        self.save(outname)
        input2 = type(self)()
        input2.load_file(outname)
        assert dict(input2) == dict(basic_input)


class ParamInput(CastepInput, ParamParser):
    pass


class CellInput(CastepInput, CellParser):
    pass
