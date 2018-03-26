# -*- encoding: utf-8 -*-
from __future__ import print_function

import os.path
import re
import sys

def main():
    # TODO: perform filename search
    filename = 'tasks.py'
    dirname = os.path.dirname(filename)
    if not dirname in sys.path:
        sys.path.insert(0, dirname)
    mod = re.sub(r"\.py$", "", filename)
    module = __import__(mod)
    entry_point_name = os.path.basename(sys.argv[0])
    default_func_name = entry_point_name.replace('-', '_')
    # lookup main function by entry_points name
    func_name = getattr(module, 'CLICK_MAPPING', default_func_name) \
        if hasattr(module, 'CLICK_MAPPING') \
        else default_func_name
    getattr(module, default_func_name)()