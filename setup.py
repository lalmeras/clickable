#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('CHANGELOG.md') as history_file:
    history = history_file.read()

test_requirements = [
]

setup(
    name='clickable',
    version='1.6',
    description=("Helper scripts to write click applications development's "
                 "environment"),
    long_description=readme + '\n\n' + history,
    long_description_content_type="text/markdown",
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
    install_requires=[
        "click==8.0.1",
        "blessings==1.7",
        "coloredlogs==15.0.1",
        "PyYAML==6.0"
        ],
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
    setup_requires=["wheel"],
)
