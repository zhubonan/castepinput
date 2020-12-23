CHANGELOG
=========

0.1.0
--------

Initial release

0.1.2
------

Fixed project home link in setup.py

0.1.3
-----

Added tab(\t) to the regex for delimiter when parsing keyword-values.

0.1.4
-----

* Fixed bugs when converting to python type. This function should be used with causion.
* Fixed a critical bug when converting cell parameters into cell vectors.

0.1.5
-----

* Fix bugs where tags with `False` values ignored when reading and wrongly set to `True` when writing. This affects input/output using python types.
