# -*- coding: utf-8 -*-

"""Top-level package for acqpack."""

__author__ = """Scott Longwell"""
__email__ = 'longwell@stanford.edu'
__version__ = '0.8.0'

import gui
import utils
from asicontroller import AsiController
from autosampler import Autosampler
from fractioncollector import FractionCollector
from manifold import Manifold
from motor import Motor

# TODO: packaging https://python-packaging.readthedocs.io/en/latest/non-code-files.html
