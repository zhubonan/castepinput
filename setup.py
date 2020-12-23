from __future__ import absolute_import
from setuptools import setup, find_packages
from os import path
import os

version = '0.1.5'
if __name__ == '__main__':

    # Check if in a CI environment
    is_tagged = False
    if os.environ.get('CI_COMMIT_TAG'):
        ci_version = os.environ['CI_COMMIT_TAG']
        is_tagged = True
    elif os.environ.get('CI_JOB_ID'):
        ci_version = os.environ['CI_JOB_ID']
    else:
        # Note in CI
        ci_version = None

    # If in a CI environment, set the version accordingly
    if ci_version:
        # If this a release, check the consistency
        if is_tagged:
            assert ci_version == version, 'Inconsistency between versions'
        else:
            version = ci_version

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
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Development Status :: 4 - Beta"
        ],
        description="A general reader/writer for CASTEP inputs",
        url="https://github.com/bz1/castepinput",
        license="MIT License",
        version=version,
        extras_require={'testing': ['pytest']},
        install_requires=["numpy", "six"])
