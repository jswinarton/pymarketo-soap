from distutils.core import setup
from setuptools import find_packages

setup(
    name='pymarketo',
    version='0.1.1',
    description='Python interface to Marketo',
    author='Jeremy Swinarton',
    author_email='jeremy@swinarton.com',
    packages=find_packages(),
    install_requires=[
        'suds >= 0.4',
    ]
)
