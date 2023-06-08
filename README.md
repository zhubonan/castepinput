A simple CASTEP input files parser/writer
==========================
This package provide a basic framework for read/write input files of CASTEP.
There is already a excellent reader/writer implemented in [ase](https://gitlab.com/ase/ase)
but they are ortentated to work with the `Atoms` and `Calculator` classes in `ase`.
It also requires a CASTEP binary to exist to work.
This package aim to provide a more generic framework with minimum dependency for
simple (but important) tasks of writing and reading inputs files of CASTEP.


Usage
------
The two classes to be used for reading/writing inputs are `ParamInput` and `CellInput`.
Keyword-value pairs can be set the same as dictionaries.
For example:

```python
from castepinput import CellInput, ParamInput, Block
# ParamInput is in fact just a subclass of OrderedDict
param = ParamInput(cut_off_energy=300, task="singlepoint")
param["opt_strategy"] = "speed"

# Use the Block class to signal that it is a BLOCK
# The following line sets the positions_abs
cell = CellInput(positions_abs=Block(["C 0 0 0", "C 1 0 0"])
```

The two classes use simple string formatting when writing out the content.
See the following code as example.
```python
cell = CellInput(snap_to_symmetry=True)

# Should give 'snap_to_symmetry : True'
cell.get_string()

# Should give 'symmetry_genreate : true'
cell['snap_to_symmetry'] = 'true'
cell.get_string()

# Not all CASTEP keyword requires a value
# Use "" as the value will result just a keyword on a line
cell['symmetry_generate'] = ''
# Should give a string with a line 'symmetry_generate'
cell.get_string()

# Set cell and positions use the set methods
cell.set_cell([10 ,10 , 10])
cell.set_positions(["O", "O"], [[0, 0, 0], [1.4, 0, 0]])
# Save to file
cell.save("O2.cell")
```

To initialize from a existing param/cell file, use the `ParamInput.from_file` method.
```python
cell = CellInput.from_file("O2.cell")
# This should give [[10, 0, 0], [0, 10, 0], [0, 0, 10]]
cell.get_cell()

# The value returned should be "" to be consistent with setting
cell["symmetry_generate"]
```

We also try to be smart and convert string into python types where it is possible.
Supported types are integer, floats and 1-d arrays made of integer/floats.
These coversions can be avoided by using `ParamInput.from_file(filename, plain=True)` when loading files.
