import logging
import os
import os.path
import pprint
import select
import subprocess
import sys
import time
from types import ModuleType

from blessings import Terminal

import yaml

logger = logging.getLogger(__name__)
stdout = logging.getLogger('.'.join(['stdout', __name__]))


class PathResolver(object):
    def __init__(self, base_element):
        if type(base_element) == ModuleType:
            self.base_path = os.path.dirname(base_element.__file__)
        elif isinstance(base_element, str):
            self.base_path = os.path.abspath(base_element)
            if not os.path.isabs(base_element):
                logger.warn('non-absolute path is resolved as {}'
                            .format(self.base_path))

    def resolve_relative(self, path):
        return os.path.normpath(os.path.join(self.base_path, path))


def load_config(click_ctx, module_name, clickables_py, conf_filename = 'clickables.yml'):
    if not hasattr(click_ctx, 'obj') or not click_ctx.obj:
        click_ctx.obj = {}
    click_ctx.obj['path_resolver'] = PathResolver(sys.modules[module_name])
    click_ctx.obj['project_root'] = os.path.dirname(clickables_py)
    conf_path = os.path.join(click_ctx.obj['project_root'], 'clickables.yml')
    if os.path.isfile(conf_path):
        with open(conf_path) as f:
            configuration = yaml.safe_load(f)
            click_ctx.obj.update(configuration)
    logger.debug('loaded configuration: \n{}'.format(pprint.pformat(click_ctx.obj)))
    click_ctx.obj['virtualenv_path'] = click_ctx.obj['ansible']['virtualenv']['path']
    return
