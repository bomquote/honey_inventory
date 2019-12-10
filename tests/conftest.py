# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""

import sys
import os
import time
import py
import pytest
from os.path import dirname as d
from os.path import abspath, join
from _pytest.tmpdir import _mk_tmp
from webtest import TestApp

root_dir = d(d(abspath(__file__)))
sys.path.append(root_dir)
