import os
from setuptools import setup, find_packages


def read(fname):
    """ Return content of specified file """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


NAME = 'disentangler'
VERSION = '1.0'

setup(
    name=NAME,
    version=VERSION,
    license='GPLv3',
    py_modules=[NAME],
    description='Simple dependency tree builder, handles forward and reverse dependencies',
    long_description=read('README.rst'),
    url='https://github.com/Outernet-Project/disentangler',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
    ],
)
