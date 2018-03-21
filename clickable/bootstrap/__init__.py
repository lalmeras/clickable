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


def setup(target_py,
          name, version='dev', description=None,
          entry_points={},
          package_dir={}, packages=[]):
    """
    Perform a setuptools setup with a minimal configuration.
    """
    project_path = os.path.dirname(target_py)
    _setup(name=name,
          version=version,
          description=description,
          package_dir={'': os.path.abspath(project_path)},
          packages=packages,
          entry_points=entry_points,
          include_package_data=False,
          zip_safe=False
    )


# TODO: allow to use a file not named setup.py
def run_setup(target_py, name, version='dev', description=None,
              entry_points={}, callback=None,
              package_dir={}, packages=[]):
    """
    Either launch a pip install -e command or perform
    python setup.py [command] related to a pip install.

    This behavior is due to the fact we want to handle the whole
    bootstrap process with a same function call.

    Environment variable CLICKABLE_BOOTSTRAP allow to detect if
    we are before pip call (absent) or after (present).
    """
    if 'CLICKABLE_BOOTSTRAP' in os.environ:
        setup(target_py, name,
              version=version, description=description,
              entry_points=entry_points,
              package_dir=package_dir, packages=packages)
    else:
        try:
            bootstrapenv = run_pip_command(target_py)
            if callback:
                callback(bootstrapenv)
        except Exception:
            log.exception('clickable: {} installation failed'.format(target_py))
    sys.exit(0)


def run_pip_command(target_py):
    """
    Perform a pip install of the targeted .py file. If file is not
    a 'setup.py' file, a setup.py proxy is created and used.
    """
    (setup_py, setup_dir) = proxy_target_py(target_py)
    python_exec = sys.executable
    python_dir = os.path.dirname(python_exec)
    environ = dict(os.environ)
    paths = environ.get('PATH', None)
    paths = paths.split(':') if paths else []
    paths.insert(0, python_dir)
    pip = [path for path in [os.path.join(i, 'pip') for i in paths] if os.path.exists(path)]
    if pip:
        pip = pip[0]
        environ['CLICKABLE_BOOTSTRAP'] = 'true'
        subprocess.check_call([pip, 'install', setup_dir], env=environ)
        bin_path = os.path.relpath(os.path.dirname(sys.executable))
        return BootstrapEnvironment(
                interpreter=sys.executable,
                activate=os.path.join(bin_path, 'activate'),
                deactivate=os.path.join(bin_path, 'deactivate'),
                requirements=subprocess.check_output([pip, 'freeze']).splitlines()
        )


def proxy_target_py(target_py):
    """
    When we do not have a setup.py as configuration file, create a fake
    temporary directory with a setup.py bound to target_py file.

    This directory cannot be used for an *editable* install as in
    this case, egg-info file is not created by python setup.py where
    pip expects it.
    """
    target_py_fn = os.path.basename(target_py)
    target_dir = os.path.dirname(target_py)

    if target_py_fn == 'setup.py':
        return (target_py_fn, target_dir)
    else:
        # TODO replace .py only at file end
        # TODO remove tmp file once install is done
        target_py_mod = target_py_fn.replace('.py', '')
        tempdir = tempfile.mkdtemp()
        setup_py = os.path.join(tempdir, 'setup.py')
        setup_dir = os.path.dirname(setup_py)
        with open(setup_py, 'w') as f:
            f.write("""
import os
import os.path
import sys

os.chdir(os.path.dirname(__file__))
sys.path.insert(0, {0})
__import__({1})
""".format(repr(os.path.abspath(target_dir)), repr(target_py_mod)))
            if log.isEnabledFor(logging.DEBUG):
                content = subprocess.check_output(setup_py)
                log.debug(content)
        return (setup_py, setup_dir)
