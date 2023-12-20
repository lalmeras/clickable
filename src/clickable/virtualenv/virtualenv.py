import glob
import json
import locale
import logging
import os.path
import shlex
import subprocess

logger = logging.getLogger(__name__)
stdout = logging.getLogger('.'.join(['stdout', __name__]))


def _virtualenv(path_resolver, virtualenv):
    """
    Initialize a virtualenv folder.

    Parameters
    ----------
    virtualenv: object
        virtualenv definition

    Virtualenv definition
    ---------------------
    path: str
        virtualenv root folder; either absolute, or relative from tasks.py file
    requirements: iterable
        list of package specs

    """
    # only create if missing
    virtualenv_path = path_resolver.resolve_relative(virtualenv['path'])
    virtualenv_path_short = virtualenv['path']
    selinux = virtualenv.get('selinux', False)
    python = virtualenv.get('python', 'python')
    if not _check_virtualenv(virtualenv_path):
        stdout.info('virtualenv: {} missing, creating...'
                    .format(os.path.basename(virtualenv_path_short)))
        # create parent folder if missing
        if os.path.dirname(virtualenv_path) \
                and not os.path.exists(os.path.dirname(virtualenv_path)):
            os.makedirs(os.path.dirname(virtualenv_path))
        # run virtualenv's creation command
        command = []
        command.append('virtualenv')
        if python:
            command.extend(['-p', python])
        command.append(virtualenv_path)
        subprocess.check_call(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # check consistency; virtualenv must be valid now
        if not _check_virtualenv(virtualenv_path):
            raise Exception('virtualenv {} creation fails'.format(virtualenv_path))
        # symlink selinux system-packages in virtualenv if needed and selinux found
        if selinux:
            _selinux(virtualenv_path)
    else:
        stdout.info('virtualenv: {} existing, skipping'
                    .format(os.path.basename(virtualenv_path_short)))

def _selinux(virtualenv_path):
    # detect virtualenv version
    python = os.path.join(virtualenv_path, 'bin', 'python')
    python_command = [
            python,
            '-c',
            'import sys, json; print(json.dumps(sys.version_info[0]))'
    ]
    output = subprocess.check_output(python_command, stderr=subprocess.STDOUT, text=True)
    version = json.loads(output)

    # search selinux from an interpreters list
    interpreters = []
    interpreters.append(python)
    # if running in anaconda, we need to search selinux
    # module in system install
    if version == 2:
        interpreters.append('/bin/python2')
        interpreters.append('/usr/bin/python2')
    else:
        interpreters.append('/bin/python3')
        interpreters.append('/usr/bin/python3')
    logger.debug('Searching selinux in: {}'.format(', '.join(interpreters)))

    # Iterate over interpreters list
    # Install from the first selinux-enabled interpreter
    selected_selinux = None
    for selinux_python in interpreters:
        # check if selinux is available
        selinux_command = [
                selinux_python,
                '-c',
                'import json; '
                + 'import selinux; '
                + 'print(json.dumps([selinux.__file__, selinux._selinux.__file__]))'
        ]
        try:
            output = subprocess.check_output(selinux_command, stderr=subprocess.STDOUT, text=True)
        except subprocess.CalledProcessError as processError:
            # selinux not available, ignore it
            logger.debug('selinux not available, ignore it ({})'.format(selinux_command))
            logger.debug(processError.output)
            continue
        except Exception:
            logger.debug('interpreter not found, skipping: {}'.format(selinux_command))
            continue
        if not output:
            logger.warn('selinux detected but not found for {}'.format(selinux_python))
        else:
            info = json.loads(output)
            location = info[0]
            so_location = info[1]
            module_location = os.path.dirname(location)
            python_site_packages = glob.glob(os.path.join(virtualenv_path, 'lib', 'python*', 'site-packages'))[0]
            target_module_location = os.path.join(python_site_packages, 'selinux')
            target_so_location = os.path.join(python_site_packages, '_selinux.so')
            if not os.path.exists(target_module_location):
                os.symlink(module_location, target_module_location)
            if not os.path.exists(target_so_location):
                os.symlink(so_location, target_so_location)
            selected_selinux = selinux_python

    # info message if installation is done, else warn message
    if selected_selinux:
        stdout.info('Selinux installed from {}'.format(selected_selinux))
    else:
        stdout.warn('No selinux installation found. Selinux not installed.')

def _check_virtualenv(virtualenv_path):
    """
    Check if virtualenv is initialized in virtualenv folder (based on
    bin/python file).

    Parameters
    ----------
    virtualenv_folder: str
        absolute path for the virtualenv root folder to check
    """
    # check <virtualenv_path>/bin/python existence
    python_bin = os.path.join(virtualenv_path, 'bin/python')
    logger.info(python_bin)
    found = False
    try:
        subprocess.check_call(
            [python_bin, '--version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        found = True
    except Exception:
        logger.debug('bin/python not found in {}'.format(python_bin),
                     exc_info=True)
    logger.info('virtualenv: {} {}'
                .format(
                    python_bin,
                    'found'
                    if found
                    else 'not found'
                )
                )
    return found


def _pip_packages(path_resolver, virtualenv):
    """
    Install pypi packages (with pip) inside a virtualenv environment.
    """
    pip_binary = os.path.join(
        path_resolver.resolve_relative(virtualenv['path']), 'bin', 'pip')
    pip_binary = os.path.normpath(pip_binary)

    # store initial state
    initial_pkglist_set = _pip_freeze(pip_binary)
    if len(initial_pkglist_set) > 0:
        logger.debug('virtualenv: pip pre-install status\n\t{}'
                     .format('\n\t'.join(initial_pkglist_set)))
    else:
        logger.debug('virtualenv: pip pre-install - no packages')

    # perform installation
    pi_args = []
    pi_args.append(pip_binary)
    pi_args.append('install')
    for package in virtualenv['requirements']:
        pi_args.append(package)

    cmd = " ".join([shlex.quote(i) for i in pi_args])
    try:
        subprocess.check_output(pi_args,
            stderr=subprocess.PIPE,
            env=_pip_env(os.environ))
    except subprocess.CalledProcessError as e1:
        raise Exception("Command {} failed with output: {}".format(cmd, e1.output)) from e1
    except Exception as e2:
        raise Exception("Command {} failed".format(cmd)) from e2
    # print some feedback about installs
    final_pkglist_set = _pip_freeze(pip_binary)
    logger.debug('virtualenv: pip post-install status\n\t{}'
                 .format('\n\t'.join(final_pkglist_set)))
    installed = set(final_pkglist_set) - set(initial_pkglist_set)
    if len(installed) > 0:
        stdout.info('virtualenv: installed or updated packages\n\t{}'
                    .format('\n\t'.join(installed)))
    else:
        stdout.info('virtualenv: no missing pip packages')


def _pip_freeze(pip_binary):
    pf_args = []
    pf_args.append(pip_binary)
    pf_args.append('freeze')
    cmd = " ".join([shlex.quote(i) for i in pf_args])
    try:
        out = subprocess.check_output(pf_args,
                stderr=subprocess.STDOUT,
                text=True)
    except subprocess.CalledProcessError as e1:
        raise Exception("Command {} failed with output: {}".format(cmd, e1.output)) from e1
    except Exception as e2:
        raise Exception("Command {} failed".format(cmd)) from e2
    pkglist = out
    pkglist_str = pkglist
    pkglist_set = set(pkglist_str.splitlines())
    return pkglist_set

def _pip_env(original_env):
    """Add PKG_CONFIG_PATH if conda is detected. original_env is not modified.
    Modified environment is the returned value. If original_env is not modified,
    it may be the returned value.
    """
    conda_prefix = original_env.get('CONDA_PREFIX', None)
    if conda_prefix is not None:
        environ = dict(original_env)
        environ.update({
            'PKG_CONFIG_PATH': os.path.join(conda_prefix, 'lib', 'pkgconfig')
        })
        return environ
    else:
        return original_env
