

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import os

setup(
    name='liam-compiler',
    version='2.5.7',
    description='A compiler for the Liam language',
    long_description=open('README.rst').read(),
    url='https://ergonomica.readthedocs.io',
    author='Liam Schumm',
    author_email='liamschumm@icloud.com',
    license='GPL-2.0',
    packages=find_packages(exclude=['tests']),
    entry_points={
        'console_scripts': [
            'liam=liam.compiler:main',
        ],
    },
)
