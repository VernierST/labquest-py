import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="labquest",
    version="1.0.0",
    author="Vernier Software and Technology",
    author_email="info@vernier.com",
    description="Library to interface with LabQuest interfaces via USB",
    license="GPL v3.0",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vernierst/labquest-py",
    packages=setuptools.find_packages(),
    package_data={'labquest': ['data/*.txt', 'data/*.dylib', 'data/*.dll']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
)
