"""
This module is a helper for cleaning .pyc/.pyo files
"""
import os


def clean():
    """
     "Remove *.pyc and *.pyo files recursively starting at current directory"
     To use, open a python console in the honey_inventory directory, import, call.
    :return:
    """
    for dirpath, dirnames, filenames in os.walk('.'):
        for filename in filenames:
            if filename.endswith('.pyc') or filename.endswith('.pyo'):
                full_pathname = os.path.join(dirpath, filename)
                print('Removing %s' % full_pathname)
                os.remove(full_pathname)