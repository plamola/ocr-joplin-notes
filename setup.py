# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages
import ocr_joplin_notes

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


requirements = [
    "numpy>=1.22.1",
    "setuptools~=60.7.0",
    "pytz>=2021.1",
    "nose>=1.3.7",
    "opencv-python>=4.5.5.62",
    "click>=8.0.3",
    "requests>=2.27.1",
    "PyPDF2>=1.26.0",
    "Pillow>=9.0.0",
    "pdf2image>=1.16.0",
    "pytesseract>=0.3.8",
]

setup_requirements = []


test_requirements = []

setup(
    name='ocr-joplin-notes',
    version=ocr_joplin_notes.__version__,
    description='Add OCR data to Joplin notes',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=ocr_joplin_notes.__author__,
    author_email=ocr_joplin_notes.__email__,
    url='https://github.com/plamola/ocr-joplin-notes',
    install_requires=requirements,
    license="MIT",
    packages=find_packages(exclude=('tests', 'docs')),
    include_package_data=True,
    keywords=["ocr-joplin-notes", "joplin", "ocr-joplin-notes"],
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    python_requires=">=3.5",
)

