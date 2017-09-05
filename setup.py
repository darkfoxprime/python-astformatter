"""The setuptools module for ASTFormatter.
"""

from setuptools import setup

from codecs import open

from astformatter import ASTFormatter

long_description = getattr(ASTFormatter, '__doc__', "").lstrip().rstrip('\n').split('\n')
if len(long_description) > 1:
    indent = len(long_description[1]) - len(long_description[1].lstrip())
    long_description[1:] = [desc[indent:] for desc in long_description[1:]]
long_description = '\n'.join(long_description).rstrip('\n')

open('README.rst', 'w').write(long_description + '\n')

setup(
    name = 'ASTFormatter' ,
    version = ASTFormatter.__version__ ,
    description = 'The ASTFormatter class accepts an AST tree and returns a valid source code representation of that tree.' ,
    long_description = long_description ,
    url = 'https://github.com/darkfoxprime/python-astformatter' ,
    # bugtrack_url = 'https://github.com/darkfoxprime/python-astformatter/issues' ,
    author = 'Johnson Earls' ,
    author_email = 'darkfoxprime@gmail.com' ,
    license = 'ISC' ,
    classifiers = [
        'Development Status :: 4 - Beta' ,
        'Intended Audience :: Developers' ,
        'Topic :: Software Development :: Libraries :: Python Modules' ,
        'License :: OSI Approved :: ISC License (ISCL)' ,
        'Programming Language :: Python :: 2.6' ,
        'Programming Language :: Python :: 2.7' ,
        'Programming Language :: Python :: 3.4' ,
    ] ,
    keywords = 'AST, source code formatter' ,
    # py_modules = ['ASTFormatter'] ,
    packages = [ 'astformatter' ] ,
    install_requires = [] ,
    package_data = {} ,
    data_files = [] ,
    entry_points = {} ,
)
