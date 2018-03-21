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
log = logging.getLogger('clickable.bootstrap')
cli = logging.getLogger('stdout.clickable')


class BootstrapEnvironment(object):
    def __init__(self, interpreter, activate, deactivate, requirements):
        self.interpreter = interpreter
        self.activate = activate
        self.deactivate = deactivate
        self.requirements = requirements


def setup(name, version='dev', description=None, entry_points={}):
    """
    Perform a setuptools setup with a minimal configuration.
    """
    _setup(name=name,
          version=version,
          description=description,
          packages=[],
          entry_points=entry_points,
          include_package_data=False,
          zip_safe=False
    )


# TODO: allow to use a file not named setup.py
def run_setup(setup_py, name, version='dev', description=None,
              entry_points={}, callback=None):
    """
    Either launch a pip install -e command or perform
    python setup.py [command] related to a pip install.

    This behavior is due to the fact we want to handle the whole
    bootstrap process with a same function call.

    Environment variable CLICKABLE_SETUP allow to detect if
    we are before pip call (false) or after (true).
    """
    if os.environ.get('CLICKABLE_SETUP', 'false') == 'true':
        setup(name, version, description, entry_points)
    else:
        try:
            bootstrapenv = run_pip_command(setup_py)
            if callback:
                callback(bootstrapenv)
            sys.exit(0)
        except Exception:
            log.exception('clickable: {} installation failed'.format(setup_py))


def run_pip_command(target_py):
    """
    Perform a pip install of the targeted .py file. If file is not
    a 'setup.py' file, a setup.py proxy is created and used.
    """
    target_py_fn = os.path.basename(target_py)
    target_dir = os.path.dirname(target_py)
    setup_py = target_py
    setup_dir = target_dir
    if target_py_fn != 'setup.py':
        # TODO replace .py only at file end
        # TODO remove tmp file once install is done
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
            if log.isEnabledFor(logging.DEBUG):
                content = subprocess.check_output(setup_py)
                log.debug(content)
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
        bin_path = os.path.relpath(os.path.dirname(sys.executable))
        return BootstrapEnvironment(
                interpreter=sys.executable,
                activate=os.path.join(bin_path, 'activate'),
                deactivate=os.path.join(bin_path, 'deactivate'),
                requirements=subprocess.check_output([pip, 'freeze']).splitlines()
        )
