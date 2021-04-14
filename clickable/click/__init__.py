# -*- encoding: utf-8 -*-

"""main is the command entry point. It search a clickables.py file in current
directory, then a no args callable from the file.

This callable is determined from:

* a callable key, built from script basename.
* an optional mapping, extracted from `clickable.py`
* an optional callable key to callable name mapping
* a lookup in `clickable.py` with the the callable name

Other rules for callable key, callable name and callable lookup behavior:

* Special chars in callable key are replaced by `_` to obtain a valid
  attribute name.
* If mapping is a `str`, callable key has no importance.
* If a dict mapping is available, callable key must be found in mapping
  keys.
* Mapping is searched in `clickable.py` with `CLICKABLE_MAPPING` name,
  `CLICK_MAPPING` as a fallback.
* if no mapping is available, callable is searched with callable key
  then `main` as a fallback."""

import collections.abc
import os
import os.path
import pprint
import re
import sys


def _clickable_debug():
    return os.environ.get("CLICKABLE_DEBUG", "").lower() in ("true", "1", "yes")


def _find_callable_mapping(module):
    """Find first valid attribute from CLICKABLE_MAPPING, CLICK_MAPPING."""
    return getattr(module, 'CLICKABLE_MAPPING', None) or \
        getattr(module, 'CLICK_MAPPING', None)


def _find_callable_name(mapping, key):
    if mapping is None:
        return key
    elif isinstance(mapping, str):
        return mapping
    elif isinstance(mapping, collections.abc.Mapping):
        return mapping.get(key, None)
    else:
        raise Exception("Mapping exists but not of expected type: {}".format(mapping))


def _get_callable_key():
    """Determine callable key from sys.argv[0]. Special chars are replaced
    by `_`."""
    result = re.sub("[^a-zA-Z0-9_]", "_", sys.argv[0])
    # prefix numeric with _
    result = re.sub("^([0-9])", "_\\1", result)
    return result


def _import(filename, loader=__import__):
    """Lookup and load `filename`."""
    if not os.path.isfile(filename):
        raise Exception("Filename {} not found.".format(filename))
    dirname = os.path.abspath(os.path.dirname(filename))
    if not dirname in sys.path:
        sys.path.insert(0, dirname)
    mod = re.sub(r"\.py$", "", filename)
    return loader(mod)


def _find_callable(module):
    """Extract callable from module. Fallback to `main` if no mapping is
    available and key is not a valid callable.

    Print error messages and
    abort if some errors are encountered. Returns false if find failed."""
    # lookup expected callable
    # script name is used as a key for lookup
    callable_key = _get_callable_key()
    mapping = _find_callable_mapping(module)
    callable_name = _find_callable_name(mapping, callable_key)
    if not isinstance(callable_name, str):
        _error("Callable name {} invalid for {}".format(callable_name, callable_key))
        _error("Candidate maping: {}".format(pprint.pprint(mapping)))
        _error("Abort!", )
        return False
    else:
        func = getattr(module, callable_name, None)
        if not func and mapping is None:
            func = getattr(module, "main", None)
        if not callable(func):
            _error("Attribute {} is not a callable: {}]".format(callable_name, func))
            _error("Abort!")
            return False
        else:
            return func


def main():
    """Load project `clickables.py` and run the expected callable.

    Callable name is defined by:

    * loading CLICKABLE_MAPPING constant, else load CLICK_MAPPING
    * if str, used as a callable name
    * if dict, used as a `sys.argv[O]` mapping to find callable name
    * if previous lookup failed, use `main` as callable name
    * else fails with a `sys.exit(2)` and an error message

    `sys.argv[0]` is modified to replace `[^-.]` by `_`. Behavior
    with other not alphabetic, not numeric chars is undetermined.

    Folder containing `clickables.py` is added to `sys.path`.
    """
    # load module
    try:
        module = _import("clickables.py")
    except Exception as e:
        _error("clickables.py cannot be loaded.")
        if _clickable_debug():
            import traceback
            traceback.print_exc(e, file=sys.stderr)
        else:
            _error(str(e))
            _error("Use CLICKABLE_DEBUG=1 to get details.")
            sys.exit(2)

    func = _find_callable(module)
    if not func:
        # Error message previously printed
        sys.exit(2)

    try:
        func()
    except Exception as e:
        if _clickable_debug():
            raise e
        else:
            _error("Uncaught error during execution: {}".format(str(e)))
            _error("Use CLICKABLE_DEBUG=1 to get details.")
            sys.exit(2)


def _error(message):
    print(message, file=sys.stderr, flush=True)
