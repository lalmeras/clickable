#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read()

setup_requirements = [
]

test_requirements = [
]

setup(
    name='clickable',
    version='1.0.dev0',
    description=("Helper scripts to write click applications development's "
                 "environment"),
    long_description=readme + '\n\n' + history,
    author="Laurent Almeras",
    author_email='lalmeras@gmail.com',
    url='https://github.com/lalmeras/clickable',
    packages=find_packages(include=['clickable', 'clickable.*']),
    entry_points={
        'console_scripts': [
            "clickable = clickable.click:main"
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    python_requires='>=3.6',
    license="BSD license",
    zip_safe=False,
    keywords='clickable',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
