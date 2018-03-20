# -*- coding: utf-8 -*-

from __future__ import print_function

import logging
import os
import os.path
import subprocess
import sys
import tempfile

from setuptools import setup as _setup

from clickable.coloredlogs import bootstrap


bootstrap()
log = logging.getLogger('clickable')


def setup(name, version='dev', description=None):
    _setup(name=name,
          version=version,
          description=description,
          packages=[],
          entry_points={
              'console_scripts': [
                  '{}=clickable.bootstrap:main'.format(name)
              ]
          },
          include_package_data=False,
          zip_safe=False
    )

# TODO: allow to use a file not named setup.py
def run_setup(setup_py, name, version='dev', description=None):
    if os.environ.get('CLICKABLE_SETUP', 'false') == 'true':
        setup(name, version, description)
    else:
        try:
            run_pip_command(setup_py, name, version, description)
            sys.exit(0)
        except Exception:
            log.exception('clickable: {} installation failed'.format(setup_py))

def run_pip_command(target_py, name, version='dev', description=None):
    target_py_fn = os.path.basename(target_py)
    target_dir = os.path.dirname(target_py)
    setup_py = target_py
    setup_dir = target_dir
    if target_py_fn != 'setup.py':
        # TODO replace .py only at file end
        target_py_mod = target_py_fn.replace('.py', '')
        tempdir = tempfile.mkdtemp()
        setup_py = os.path.join(tempdir, 'setup.py')
        setup_dir = os.path.dirname(setup_py)
        with open(setup_py, 'w') as f:
            f.write("""
import sys
import os

sys.path.insert(0, {0})
__import__({1})
""".format(repr(os.path.abspath(target_dir)), repr(target_py_mod)))
        subprocess.check_call(['cat', setup_py])
    python_exec = sys.executable
    python_dir = os.path.dirname(python_exec)
    environ = dict(os.environ)
    paths = environ.get('PATH', None)
    paths = paths.split(':') if paths else []
    paths.insert(0, python_dir)
    pip = [path for path in [os.path.join(i, 'pip') for i in paths] if os.path.exists(path)]
    if pip:
        pip = pip[0]
        environ['CLICKABLE_SETUP'] = 'true'
        subprocess.check_call([pip, 'install', '-e', setup_dir], env=environ)


def main():
    print('success')

          
