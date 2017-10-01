from __future__ import print_function  # pylint: disable=unused-import

import logging
import os
import os.path

from clickable.utils import interactive
from clickable.utils import oneline_run


logger = logging.getLogger(__name__)
stdout = logging.getLogger('stdout.{}'.format(__name__))


def sphinx_script(ctx, virtualenv, script, args=[], env=None, clear_env=False):
    script_path = os.path.join(ctx.obj['project_root'],
                               virtualenv['path'],
                               'bin',
                               script)
    if not os.path.exists(script_path):
        raise Exception('sphinx: {} not found'.format(script_path))
    if not os.access(script_path, os.X_OK):
        raise Exception('sphinx: {} found but not executable'
                        .format(script_path))
    logger.debug('sphinx: found executable {}'.format(script_path))
    process_args = []
    process_args.append(script_path)
    process_args.extend(args)
    interactive(process_args, clear_env=clear_env, env=env)


def sphinx_clean(ctx, virtualenv, documentation_path):
    sphinx_build_path = os.path.join(ctx.obj['project_root'],
                                     documentation_path,
                                     'build')
    items = [item for item in os.listdir(sphinx_build_path)
             if item not in ['.', '..', '.gitkeep']]
    if len(items) == 0:
        stdout.info('sphinx.clean: no files to clean')
        return
    stdout.info('sphinx.clean: cleaning {}'.format(' '.join(items)))
    args = []
    args.extend(['rm', '-rf'])
    args.extend([os.path.normpath(os.path.join(sphinx_build_path, item))
                 for item in items])
    oneline_run(args)
