from .virtualenv import _virtualenv
from .virtualenv import _pip_packages


def virtualenv(path_resolver, virtualenv):
    _virtualenv(path_resolver, virtualenv)
    _pip_packages(path_resolver, virtualenv)
