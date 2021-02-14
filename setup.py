# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# with open('LICENSE') as f:
#     license = f.read()


setup_requirements = [
    "click",
    "requests",
    "setuptools",
    "PyPDF2",
    "Pillow",
    "pdf2image",
    "pytesseract",
    "opencv-python",
    "numpy",
]

test_requirements = []

setup(
    name='ocr-joplin-notes',
    version='0.1.2',
    description='Add OCR data to Joplin notes',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Matthijs Dekker',
    author_email='joplin-development@dekkr.nl',
    url='https://github.com/plamola/ocr-joplin-notes',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    include_package_data=True,
    keywords=["ocr-joplin-notes", "joplin", "ocr-joplin-notes"],
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
)

