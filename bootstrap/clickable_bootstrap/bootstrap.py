#! /bin/env python2
# -*- encoding: utf-8 -*-
# vim: tabstop=2 shiftwidth=2 expandtab ai

from __future__ import print_function, unicode_literals

#
# Global warning: use explicitly-indexed .format() ({0}, {1}) so
# that script is compatible with python 2.6.
#

import argparse
import os
import os.path
import pipes
import shlex
import shutil
import subprocess
import sys
import tempfile

description = \
"""
boostrap.py install a working conda or virtualenv environment.
"""


MINICONDA_INSTALLER_URL = 'https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh'


def run(args, debug=False, env=None):
  """Run a command, with stdout and stderr connected to the current terminal.
  Log command if debug=True.
  """
  if debug:
    # python2.6: index obligatoire
    print('[cmd] {0}'.format(' '.join([pipes.quote(i) for i in args])), file=sys.stderr)
    if env:
      print('[cmd] env={0}'.format(' '.join(['{0}={1}'.format(k, v) for k,v in env])), file=sys.stderr)
  subprocess.check_call(args, env=env)


def download(url, debug=False):
  """Download a file and return tuple of (fd, abspath).
  Caller is responsible for deleting file.
  Exception if download cannot be done.
  """
  # Miniconda script raise an error if script is not called something.sh
  (handle, abspath) = tempfile.mkstemp(prefix='bootstrap', suffix='.sh')
  os.close(handle)
  try:
    args = ['curl', '-v' if debug else None, '-o', abspath, url]
    args = [i for i in args if i]
    run(args, debug=debug)
  except Exception as e:
    if not debug:
      try:
        os.remove(abspath)
      except:
        print('[ERROR] Failing to delete {0}'.format(abspath), file=sys.stderr)
    else:
      print('[DEBUG] Keeping file {}'.format(abspath), file=sys.stderr)
    raise Exception('Failed to download {0}. {1}'.format(url, str(e)))
  return (handle, abspath)


def ansible_playbook(prefix, ansible_prefix, playbook, debug=False):
  ansible_args = [os.path.join(prefix, 'bin', 'ansible-playbook'), playbook]
  ansible_config = os.path.join(ansible_prefix, 'ansible.cfg')
  run(ansible_args, env={'ANSIBLE_CONFIG': ansible_config}, debug=debug)


def bootstrap(reset=False, debug=False):
  """Delete existing Miniconda if reset=True.
  Print verbose output (stderr of commands and debug messages) if debug=True.
  """
  home = os.getenv('HOME')
  prefix = os.path.join(home, '.miniconda2')
  if reset:
    if os.path.exists(prefix):
      print("[INFO] Destroying existing env: {0}.".format(prefix), file=sys.stderr)
      shutil.rmtree(prefix)
  miniconda_script = None
  miniconda_install = True
  if os.path.exists(prefix):
    print("[INFO] Env {0} already exists; use --reset to destroy and recreate it.".format(prefix), file=sys.stderr)
    miniconda_install = False
  try:
    if miniconda_install:
      # Download Miniconda
      (_, miniconda_script) = download(MINICONDA_INSTALLER_URL, debug=debug)
      # Run Miniconda
      miniconda_args = ['/bin/bash', miniconda_script, '-u', '-b', '-p', prefix]
      run(miniconda_args, debug=debug)
    # Upgrade pip
    pip_upgrade_args = [os.path.join(prefix, 'bin', 'pip'), 'install', '--upgrade', 'pip']
    run(pip_upgrade_args, debug=debug)
    ## Install ansible 2.4
    #pip_install_ansible_args = [os.path.join(prefix, 'bin', 'pip'), 'install', '-I', 'ansible==2.4.2.0']
    #run(pip_install_ansible_args, debug=debug)
    ## Install git >=2.17
    #pip_install_ansible_args = [os.path.join(prefix, 'bin', 'conda'), 'install', '-y', 'git>=2.17']
    #run(pip_install_ansible_args, debug=debug)
    # Activate Miniconda env
    print("[INFO] Env {0} initialized.".format(prefix), file=sys.stderr)
    # TODO: env activation (?)
  except Exception as e:
    print('[ERROR] Bootstrap failure: {0}'.format(str(e)))
    if not debug:
      if miniconda_script:
        try:
          os.remove(miniconda_script)
        except:
          print('[ERROR] Failing to delete {0}'.format(miniconda_script), file=sys.stderr)
    else:
      if miniconda_script:
        print('[DEBUG] Keeping file {0}'.format(miniconda_script), file=sys.stderr)


def parser():
  """Command line parsing"""
  cmd = argparse.ArgumentParser(description='Initialize a conda or virtualenv environment.')
  cmd.add_argument('--reset', dest='reset', action='store_true')
  cmd.add_argument('--debug', dest='debug', action='store_true')
  return cmd


if __name__ == '__main__':
  args = parser().parse_args()
  bootstrap(**vars(args))
