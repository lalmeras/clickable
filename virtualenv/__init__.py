from .virtualenv import _virtualenv
from .virtualenv import _pip_packages


def virtualenv(ctx, virtualenv):
    _virtualenv(ctx, virtualenv)
    _pip_packages(ctx, virtualenv)
