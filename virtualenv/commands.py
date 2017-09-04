import click
from click.globals import get_current_context

from . import virtualenv


class VirtualenvCommand(click.Command):

    def __init__(self, *args, **kwargs):
        original_callback = kwargs['callback']

        def callback(*args, **kwargs):
            def virtualenv_call(path_resolver, configuration):
                virtualenv(path_resolver, configuration)
            original_callback(get_current_context(), virtualenv_call,
                              *args, **kwargs)
        kwargs['callback'] = callback
        super(VirtualenvCommand, self).__init__(*args, **kwargs)
