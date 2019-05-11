from __future__ import absolute_import
from setuptools import setup, find_packages
from os import path

if __name__ == '__main__':

    README_PATH = path.join(path.dirname(__file__), "README.md")
    with open(README_PATH) as f:
        long_desc = f.read()
    setup(
        include_package_data=True,
        packages=find_packages(),
        long_description=long_desc,
        long_description_content_type='text/markdown',
        name='castepinput',
        author='Bonan Zhu',
        author_email='bon.zhu@protonmail.com',
        classifiers=[
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3.5",
            "Development Status :: 4 - Beta"
        ],
        description="A general reader writer for CASTEP inputs",
        url="https://gitlab.com/bz1/castepinput",
        license="MIT License",
        version="0.1.4",
        install_requires=["numpy", "six"])
