# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='ocr-joplin-notes',
    version='0.1.0',
    description='Add OCR data to Joplin notes',
    long_description='See the README.md',
    author='Matthijs Dekker',
    author_email='joplin-development@dekkr.nl',
    url='https://github.com/plamola/ocr-joplin-notes',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

