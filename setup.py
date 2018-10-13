from setuptools import setup, find_packages

if __name__ == '__main__':

    with open("Readme.md") as f:
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
            "Programming Language:: Python", "Development Status :: 4- Beta"
        ],
        description="A general reader writer for CASTEP inputs",
        url="https://gitlab.com/bz1/castepiputs",
        license="MIT License",
        version="0.1.0",
        install_requires=["numpy"])
