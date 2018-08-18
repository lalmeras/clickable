"""One-liner initialization of clickable tooling"""

__version__ = "0.9.0"


import os.path
import ast

import clickable_logging

clog = clickable_logging.bootstrap(__name__, 'bootstrap')


def _search_configuration(path, files=['clickable.py']):
    if not os.path.isdir(path):
        raise ConfigurationNotFound("path {} does not exist".format(path))
    current_path = path
    next_path = None
    stop = False
    while True:
        for f in files:
            search = os.path.join(path, f)
            if os.path.isfile(search):
                clog.log.info('Trying {} configuration file'.format(search))
                try:
                    configuration = _parse_configuration(search)
                    return configuration
                except ConfigurationSyntaxError:
                    clog.log.error("configuration {} cannot be loaded".format(search), exc_info=True)
                    raise ConfigurationNotFound("configuration {} cannot be loaded".format(search))
            else:
                clog.log.debug('Skipping not existing {} configuration file'.format(search))
        # go up folder tree
        next_path = os.path.dirname(current_path)
        if os.path.normpath(next_path) == os.path.normpath(current_path):
            # stop if we no longer go up
            break
        current_path = next_path


def _parse_configuration(conf_file):
    """
    Parse a python file for basic configuration.
    """
    try:
        with open(conf_file) as stream:
            clog.log.info('Parsing %s configuration file' % (conf_file,))
            ast_tree = ast.parse(''.join(stream.readlines()))
            values = _find_ast_values(ast_tree, 'clickable_bootstrap_spec')
            if not 'clickable_bootstrap_spec' in values.keys():
                raise ConfigurationSyntaxError("{} not found in {}".format("clickable_bootstrap_spec", conf_file))
            return values
    except Exception:
        clog.log.error("configuration {} cannot be parsed".format(conf_file), exc_info=True)
        raise ConfigurationSyntaxError("error parsing {}".format(conf_file))


def _find_ast_values(ast_tree, *args):
    """
    Find arg = "string value" in ast_tree ; only first level is considered.

    A dict of arg: value is returned. Caller must verify in returned dict if all
    the needed values are found.

    Raise an error if configuration name is found but value is not a string value.
    """
    result = dict()
    for node in ast.iter_child_nodes(ast_tree):
        ignored = True
        if isinstance(node, ast.Assign):
            clog.log.info("found assign node {} at {}:{}".format(node, node.lineno, node.col_offset))
            for arg in args:
                # TODO: multiple assignment ?
                if isinstance(node.targets[0], ast.Name):
                    if node.targets[0].id == arg:
                        clog.log.info("found assign node {} for {} at {}:{}".format(node, arg, node.lineno, node.col_offset))
                        if not isinstance(node.value, ast.Str):
                            raise ConfigurationSyntaxError("only String supported for {} at {}:{}", arg, node.lineno, node.col_offset)
                        result[arg] = node.value.s
                        clog.log.info("node {} = '{}' found at {}:{}".format(arg, result[arg], node.lineno, node.col_offset))
                        ignored = False
        if ignored:
            clog.log.debug("ignored node {}".format(node))
    for arg in args:
        not_found = []
        if arg not in result.keys():
            not_found.append(arg)
    if not_found:
        clog.log.debug("configurations [{}] not found".format(', '.join([i for i in not_found])))
    return result


class ConfigurationNotFound(Exception):
    pass


class ConfigurationSyntaxError(Exception):
    pass
