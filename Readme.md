CASTEP INPUT parser/writer
==========================
This package provide basic functions to read/write input files of CASTEP.
There is already a good reader/writer implemented in `ASE` but they are ortentated to work
with the `Atoms` and `Calculator` instance.
This package aim to provide a more generic framework of writing and reading CASTEP's seed files.

Usage
------
The two classes to be used for reading/writing inputs are `ParamInput` and `CellInput`.
Keyword-value pairs can be set the same as dictionaries.
For example:
```python
# Same usage as dictionary
param = ParamInput(cut_off_energy=300, task="singlepoint")
param["opt_strategy"] = "speed"

# For block we use the Block instance to signal that it is a BLOCK
cell = CellInput(positions_abs=Block(["C 0 0 0", "C 1 0 0"])
```

The two class uses simple string formatting when writing out the content.
```python
cell = CellInput(symmetry_generate=True)
cell.get_string()
# Should give 'symmetry_generate : True'

cell = CellInput(symmetry_generate='true')
cell.get_string()
# Should give 'symmetry_genreate : true'
```
Input files can be write out using `self.save` method.

To initialize from a existing param/cell file, use the `ParamInput.from_file` method.
For CellInput, parsed cell vectors, atomic positions and be accessed by 
`get_cell` and `get_positions` methods.
We do try to be smart and convert string into python types where it is possible.
Supported types are integer, floats and 1-d arrays made of integer/floats.
These coversions can be avoided by using `BasicParser` to read the files, values of each
keywords in this case are kepts as strings.
