import logging
import os
import os.path
import select
import subprocess
import sys
import time
from types import ModuleType

from blessings import Terminal

import six

logger = logging.getLogger(__name__)
stdout = logging.getLogger('.'.join(['stdout', __name__]))

__terminal_width = None


class PathResolver(object):
    def __init__(self, base_element):
        if type(base_element) == ModuleType:
            self.base_path = os.path.dirname(base_element.__file__)
        elif isinstance(base_element, six.string_types):
            self.base_path = os.path.abspath(base_element)
            if not os.path.isabs(base_element):
                logger.warn('non-absolute path is resolved as {}'
                            .format(self.base_path))

    def resolve_relative(self, path):
        return os.path.normpath(os.path.join(self.base_path, path))


def _terminal_width():
    global __terminal_width
    if __terminal_width is None:
        try:
            t = Terminal()
            __terminal_width = t.width
            logger.info('virtualenv: detected terminal width {}'
                        .format(t.width))
        except Exception:
            __terminal_width = 0
            logger.warn('virtualenv: terminal width cannot be determined')
    return __terminal_width if __terminal_width != 0 else None


def oneline_run(args):
    return run(args, oneline_mode=True)


def run(args, oneline_mode=False, env=None, clear_env=False):
    p_env = dict(os.environ)
    if env is not None:
        if clear_env:
            p_env = env
        else:
            p_env.update(env)
    p = subprocess.Popen(args,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         env=p_env)
    logger.debug('utils.oneline_run: running {}'
                 .format(' '.join(args)))
    return _subprocess_run(p, oneline_mode=oneline_mode)


def interactive(args, env=None, clear_env=False):
    p_env = dict(os.environ)
    if env is not None:
        if clear_env:
            p_env = env
        else:
            p_env.update(env)
    logger.debug('utils.interactive: running {}'
                 .format(' '.join(args)))
    subprocess.check_call(args, env=p_env)


def _subprocess_run(subprocess,
                    return_stdout=True,
                    return_stderr=True,
                    write_stdout=sys.stdout,
                    write_stderr=sys.stdout,
                    oneline_mode=True,
                    oneline_timing=.01):
    if _terminal_width() is None and oneline_mode:
        logger.warn('online_mode disabled as terminal width is not found')
        oneline_mode = False
    if oneline_mode and write_stdout != write_stderr:
        raise Exception('write_stdout == write_stderr needed for oneline_mode')
    whole = ''
    curlines = {'stdout': None, 'stderr': None}
    waiting = []
    streams = {
        subprocess.stdout.fileno(): {
            'stream': 'stdout',
            'return': return_stdout,
            'write': write_stdout,
            'pipe': subprocess.stdout
        },
        subprocess.stderr.fileno(): {
            'stream': 'stderr',
            'return': return_stderr,
            'write': write_stderr,
            'pipe': subprocess.stderr
        },
    }
    while True:
        ret = select.select(streams.keys(), [], [])

        for fd in ret[0]:
            stream_desc = streams[fd]
            stream = streams[fd]['stream']
            output = stream_desc['pipe'].read()
            if stream_desc['return']:
                whole += output
            if not oneline_mode and stream_desc['write'] is not None:
                stream_desc['write'].write(output)
            if oneline_mode:
                _handle_oneline(waiting, curlines, stream, output)

            # in oneline_mode, output only one line by cycle
            if oneline_mode and len(waiting) > 0:
                _write_line(waiting.pop(0), write_stdout, oneline_timing)

        if oneline_mode:
            for w in waiting:
                _write_line(w, write_stdout, oneline_timing)
            _write_line('', write_stdout, oneline_timing)

        # end loop when program ends
        if subprocess.poll() is not None:
            break
    return whole


def _handle_oneline(waiting, curlines, stream, output):
    # split output by lines
    splitted = output.splitlines(True)
    # if a line waits for its end,
    # append first to partial
    if curlines[stream] is not None:
        curlines += splitted.pop(0)
        # if partial line is ended, switch it to waiting
        if curlines[stream].endswith('\n'):
            waiting.append(curlines[stream])
            curlines[stream] = None
    # if last line is not complete, switch it to partial
    if len(splitted) > 0 and not splitted[-1].endswith('\n'):
        curlines['stdout'] = splitted.pop(-1)
    # push all complete lines to waiting
    waiting.extend(splitted)


def _write_line(waiting, stream, timing):
    time.sleep(timing)
    # in oneline mode, only stdout is used
    # print with space padding
    width = _terminal_width()
    pattern = '{:%d.%d}' % (width, width)
    stream.write(pattern
                 .format(waiting.replace('\n', '')))
    stream.write('\r')
    stream.flush()
