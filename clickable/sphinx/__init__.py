import logging
import os
import os.path
import subprocess

import click

from clickable.virtualenv import virtualenv

logger = logging.getLogger(__name__)
stdout = logging.getLogger('stdout.{}'.format(__name__))


def sphinx_click_group(click_group, sphinx_provider,
                       virtualenv_provider=None, path_provider=None):
    if not path_provider:
        path_provider = lambda ctx: ctx.obj['path_resolver']
    if not virtualenv_provider:
        virtualenv_provider = lambda ctx: sphinx_provider(ctx)['virtualenv']

    @click_group.command()
    @click.pass_context
    def clean(ctx):
        virtualenv(path_provider(ctx), virtualenv_provider(ctx))
        sphinx_clean(path_provider(ctx),
                     sphinx_provider(ctx)['documentation_path'])

    @click_group.command()
    @click.argument('target')
    @click.pass_context
    def build(ctx, target):
        virtualenv(path_provider(ctx), virtualenv_provider(ctx))
        sphinx_build(path_provider(ctx), sphinx_provider(ctx),
                     virtualenv_provider(ctx), target)

    @click_group.command()
    @click.pass_context
    def live(ctx):
        virtualenv(path_provider(ctx), virtualenv_provider(ctx))
        sphinx_live(path_provider(ctx), sphinx_provider(ctx),
                    virtualenv_provider(ctx))

    @click_group.command()
    @click.option('--project', help='project name')
    @click.option('--author', help='author')
    @click.option('--version', help='version')
    @click.option('--language', help='language (fr, en, ...)')
    @click.option('--epub', is_flag=True, default=False, help='enable epub')
    @click.pass_context
    def quickstart(ctx, project, author, version, language, epub):
        virtualenv(path_provider(ctx), virtualenv_provider(ctx))
        sphinx_quickstart(path_provider(ctx), sphinx_provider(ctx),
                          virtualenv_provider(ctx),
                          project, author, version, language, epub)

def sphinx_script(path_resolver, virtualenv_config, script, args=None):
    script_path = path_resolver.resolve_relative(
        os.path.join(virtualenv_config['path'], 'bin', script))
    if not os.path.exists(script_path):
        raise Exception('sphinx: {} not found'.format(script_path))
    if not os.access(script_path, os.X_OK):
        raise Exception('sphinx: {} found but not executable'
                        .format(script_path))
    logger.debug('sphinx: found executable {}'.format(script_path))
    process_args = []
    process_args.append(script_path)
    if args:
        process_args.extend(args)
    env = dict(os.environ)
    env['PATH'] = ':'.join([
        path_resolver.resolve_relative(
            os.path.join(virtualenv_config['path'], 'bin')),
        os.environ['PATH']
    ])
    subprocess.check_call(process_args, env=env)


def sphinx_clean(path_resolver, documentation_path):
    sphinx_build_path = path_resolver.resolve_relative(
        os.path.join(documentation_path, 'build'))
    items = [item for item in os.listdir(sphinx_build_path)
             if item not in ['.', '..', '.gitkeep']]
    if not items:
        stdout.info('sphinx.clean: no files to clean')
        return
    stdout.info('sphinx.clean: cleaning {}'.format(' '.join(items)))
    args = []
    args.extend(['rm', '-rf'])
    args.extend([os.path.normpath(os.path.join(sphinx_build_path, item))
                 for item in items])
    subprocess.check_call(args)


def sphinx_build(path_resolver, sphinx_config, virtualenv_config, target):
    """
    Build TARGET sphinx delivery (html, singlepage, ...)
    """
    documentation_path = sphinx_config['documentation_path']
    sphinx_source_path = path_resolver.resolve_relative(
        os.path.join(documentation_path, 'source'))
    sphinx_build_path = path_resolver.resolve_relative(
        os.path.join(documentation_path, 'build', 'html'))
    args = []
    args.extend(['-b', target])
    args.append(sphinx_source_path)
    args.append(sphinx_build_path)
    sphinx_script(path_resolver, virtualenv_config,
                  'sphinx-build', args)


def sphinx_live(path_resolver, sphinx_config, virtualenv_config):
    """
    Live-build sphinx delivery (html, singlepage, ...)
    """
    documentation_path = sphinx_config['documentation_path']
    sphinx_source_path = path_resolver.resolve_relative(
        os.path.join(documentation_path, 'source'))
    sphinx_build_path = path_resolver.resolve_relative(
        os.path.join(documentation_path, 'build', 'html'))
    args = []
    args.extend(['--ignore', '*.swp'])
    args.extend(['--ignore', '*.log'])
    args.extend(['--ignore', '*~'])
    args.extend(['-b', 'html'])
    args.append(sphinx_source_path)
    args.append(sphinx_build_path)
    sphinx_script(path_resolver, virtualenv_config, 'sphinx-autobuild', args)


def sphinx_quickstart(path_resolver, sphinx_config, virtualenv_config,
                      project, author, version, language, epub):
    args = []
    args.append('-q')
    args.append('--suffix=.rst')
    args.append('--suffix=.md')
    args.append('--master=index.rst')
    args.append('--sep')
    args.append('--ext-todo')
    args.append('--no-makefile')
    args.append('--no-batchfile')
    args.append('--release={}'.format(version))
    args.append('--project={}'.format(project))
    args.append('--author={}'.format(author))
    args.extend(['-v', version])
    args.extend([
        '-d',
        'path={}'.format(sphinx_config['documentation_path'])
    ])
    args.extend(['-d', 'language={}'.format(language)])
    sphinx_script(path_resolver, virtualenv_config, 'sphinx-quickstart', args)
