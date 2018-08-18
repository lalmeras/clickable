"""Process management for clickable"""

__version__ = "0.9.0"

import os
import select
import subprocess
import sys
import time

from blessings import Terminal

import clickable_logging


__terminal_width = None
clog = clickable_logging.bootstrap(__name__, output_name="process")


def _terminal_width():
    """
    Compute terminal width if needed, store it as a module global variable
    and return value.

    If computation fails, set 0 for global, return None, and log
    a warn message.
    """
    global __terminal_width
    if __terminal_width is None:
        try:
            t = Terminal()
            __terminal_width = t.width
            clog.log.info("detected terminal width {}".format(t.width))
        except Exception:
            __terminal_width = 0
            clog.log.warn("terminal width cannot be determined", exc_info=True)
    return __terminal_width if __terminal_width != 0 else None


def oneline_run(args, env=None, clear_env=False):
    """
    Launch a command (args array). All output is collapsed to a
    one-line output (each line is printed and deleted).
    """
    return run(args, oneline_mode=True, env=env, clear_env=clear_env)


def run(args, oneline_mode=False, env=None, clear_env=False):
    """
    Launch a command (args array).

    :param list args: command to launch ; first parameter is the executable,
    followed by arguments
    :param bool oneline_mode: True if process output is collapsed to a
    one-line output (each line is printed then deleted)
    :param dict env: use a custom env
    :param dict clear_env: if True, launched processed does not inherit
    its environment
    """
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
    command = _log_command(args, env)
    clog.stderr.info('command launched: {}'.format(command))
    if not clear_env:
        clog.stderr.debug('inherited environment: %s' % (pprint.pformat(p_env),))
    try:
        return _subprocess_run(p, oneline_mode=oneline_mode)
    finally:
        clog.stderr.debug('command done: {}'.format(command))


def _log_command(args, env):
    command = ''
    command += ' '.join("%s=%s" % (i, shlex.quote(j)) for i, j in env.items())
    command += ' '
    command += ' '.join([shlex.quote(arg) for arg in args])
    return command


def interactive(args, env=None, clear_env=False):
    """
    Launch command in an interactive mode (process is bound to python
    stdin, stdout and stderr.

    Command result must be 0.
    """
    p_env = dict(os.environ)
    if env is not None:
        if clear_env:
            p_env = env
        else:
            p_env.update(env)
    clog.stderr.info('command launched: {}'
                 .format(' '.join(args)))
    if not clear_env:
        clog.stderr.debug('inherited environment: %s' % (pprint.pformat(p_env),))
    try:
        subprocess.check_call(args, env=p_env)
    finally:
        clog.stderr.debug('command done: {}'.format(command))


def _subprocess_run(subprocess,
                    return_stdout=True,
                    return_stderr=True,
                    write_stdout=sys.stderr,
                    write_stderr=sys.stderr,
                    oneline_mode=True,
                    oneline_timing=.01):
    """
    Launch a command. Output handling behavior is controlled by oneline_mode.
    """
    if _terminal_width() is None and oneline_mode:
        clog.stderr.warn('online_mode disabled as terminal width is not found')
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
        # wait for stream output
        ret = select.select(streams.keys(), [], [])

        for fd in ret[0]:
            stream_desc = streams[fd]
            stream = streams[fd]['stream']
            # read stream
            output = stream_desc['pipe'].read()
            # store output if *return*
            if stream_desc['return']:
                whole += output
            if not oneline_mode and stream_desc['write'] is not None:
                # directly write to output if *write*
                stream_desc['write'].write(output)
            if oneline_mode:
                # write in one-line mode
                _handle_oneline(waiting, curlines, stream, output)

            # in oneline_mode, output only one line by cycle
            if oneline_mode and len(waiting) > 0:
                _write_line(waiting.pop(0), write_stdout, oneline_timing)

        if oneline_mode:
            # process remaining lines
            for w in waiting:
                _write_line(w, write_stdout, oneline_timing)
            _write_line('', write_stdout, oneline_timing)

        # end loop when program ends
        if subprocess.poll() is not None:
            break
    return whole


def _handle_oneline(waiting, curlines, stream, output):
    """
    Handle incomplete line case. From output (last read output
    from process) read from stream (stdout or stderr), append
    it to any unfinished line in curlines, and append the new
    complete lines to waiting

    Store any unfinished line in curlines[stream]

    :param list waiting: lines waiting to be completed
    :param dict curlines: stdout and stderr buffers
    :param dict stream: identification of source stream (stdout or stderr)
    :param binary output: output to print
    """
    # split output by lines
    splitted = output.splitlines(True)
    # if a line waits for its end append first to partial
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


def _write_line(lines, stream, timing):
    """
    Write a line in one-line mode: wait for *timing* ms, then
    print lines, truncated at terminal_width.

    Printed line will be deleted at the next output printing time,
    due to the terminating \\r char.
    """
    time.sleep(timing)
    # in oneline mode, only stdout is used
    # print with space padding
    width = _terminal_width()
    pattern = '{:%d.%d}' % (width, width)
    stream.write(pattern.format(lines.replace('\n', '')))
    stream.write('\r')
    stream.flush()
