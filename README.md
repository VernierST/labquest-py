# labquest

A Python module for reading from [Vernier LabQuest® interfaces](https://www.vernier.com/products/labquest/) connected to USB. The module has been tested on Windows 10, macOS, and various Linux distros. The module should work with any of these LabQuest interfaces:
 * [LabQuest Mini](https://www.vernier.com/product/labquest-mini/)
 * [LabQuest Stream](https://www.vernier.com/product/labquest-stream/)
 * [LabQuest 3](https://www.vernier.com/product/labquest-3/)
 * [LabQuest 2](https://www.vernier.com/product/labquest-2/)
 * [LabQuest](https://www.vernier.com/downloads/original-labquest-updates/)

Take a look at the [labquest-examples repository](https://github.com/VernierST/labquest-examples/tree/main/python) for ideas and a number of helpful examples.

## Requirements

For Windows computers, you must have the appropriate USB drivers installed. The easiest way to do this is to run the free [Vernier Graphical Analysis™](https://www.vernier.com/products/graphical-analysis/free/) installer.

The following Python modules are required for `labquest`. They will be installed automatically as dependencies when installing `labquest` via pip.

* TBD

## Installation

Automatically install all the dependencies for both USB and native BLE.
```bash
pip install godirect
```

## Installation and Usage

Go to our [Getting Started with Vernier LabQuest and Python document](https://github.com/VernierST/labquest-examples/blob/main/python/readme.md) for detailed information regarding installation and usage of the labquest module.

## License

GNU General Public License v3 (GPLv3)

Vernier products are designed for educational use. Our products are not designed nor are they recommended for any industrial, medical, or commercial process such as life support, patient diagnosis, control of a manufacturing process, or industrial testing of any kind.

## Maintainer

Generate pydocs from the docs folder with:
```
python3 -m pydoc -w labquest
python3 -m pydoc -w labquest.labquest_init_functions
# etc
```

Upload to the PyPI test server:
```
python3 setup.py sdist bdist_wheel 
python3 -m twine upload --repository testpypi dist/*
```

Upload to the real PyPi server:
```
python3 setup.py sdist bdist_wheel
python3 -m twine upload dist/*
```