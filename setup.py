#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

install_requirements = [
    # put package requirements here
    'jupyter',
    'ipywidgets==6.0.0',
    'numpy',
    'pandas',
    'matplotlib',
    'opencv-python',
    'opencv-contrib-python',
    'pillow',
    'pymodbus',
    'pyserial',
    'PyYAML',
]

setup_requirements = [
    'pytest-runner',
    # put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    'pytest',
    # put package test requirements here
]

setup(
    name='acqpack',
    version='1.2.0',
    description="Library for instrument control and automated data acquisition",
    long_description=readme + '\n\n' + history,
    author="Scott Longwell",
    author_email='longwell@stanford.edu',
    url='https://github.com/fordycelab/acqpack',
    packages=find_packages(include=['acqpack']),
    include_package_data=True,
    install_requires=install_requirements,
    license="MIT license",
    zip_safe=False,
    keywords='acqpack',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        # 'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.3',
        # 'Programming Language :: Python :: 3.4',
        # 'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
