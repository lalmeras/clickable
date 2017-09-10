import logging
import os.path
import subprocess

from clickable.utils import _subprocess_run

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
    if not _check_virtualenv(virtualenv_path):
        stdout.info('virtualenv: {} missing, creating...'
                    .format(os.path.basename(virtualenv_path_short)))
        # create parent folder if missing
        if os.path.dirname(virtualenv_path) \
                and not os.path.exists(os.path.dirname(virtualenv_path)):
            os.makedirs(os.path.dirname(virtualenv_path))
        # run virtualenv's creation command
        p = subprocess.Popen(['virtualenv', virtualenv_path],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        _subprocess_run(p)
        # check consistency; virtualenv must be valid now
        if not _check_virtualenv(virtualenv_path):
            raise Exception('virtualenv {} creation fails'
                            .format(virtualenv_path))
    else:
        stdout.info('virtualenv: {} existing, skipping'
                    .format(os.path.basename(virtualenv_path_short)))


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
    p = None
    try:
        p = subprocess.Popen(
            [python_bin, '--version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        _subprocess_run(p)
    except Exception:
        logger.debug('bin/python not found in {}'.format(python_bin),
                     exc_info=True)
    logger.info('virtualenv: {} {}'
                .format(
                    python_bin,
                    'found'
                    if p is not None and p.returncode == 0
                    else 'not found'
                )
                )
    return p is not None and p.returncode == 0


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

    p = subprocess.Popen(pi_args,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    pi_out = _subprocess_run(p)
    if p.returncode != 0:
        raise Exception(pi_out)

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
    p = subprocess.Popen(pf_args,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out = _subprocess_run(p)
    if p.returncode != 0:
        raise Exception(out)
    pkglist = out
    pkglist_str = unicode(pkglist, "utf-8")
    pkglist_set = set(pkglist_str.splitlines())
    return pkglist_set
