"""
Test setup.py
"""

import unittest
from src.core.setup import setup_spaces
from shutil import rmtree
from os.path import split, abspath, dirname, isdir, join, exists
from os import environ
from sys import path as syspath


class test_SetupSpaces(unittest.TestCase):
    """
    Test setup_spaces method from src.core.setup
    """
    @classmethod
    def setUpClass(cls):
        cls.project = 'ttest'
        cls.machine = 'ttest'
        filedir, filename = split(abspath(__file__))
        cls.projectdir = join(dirname(dirname(filedir)),
                              'project', cls.project)
        cls.machinedir = join(dirname(dirname(filedir)),
                              'platform', cls.machine)
        PATH = environ['PATH']
        for p in PATH.split(':'):
            if '/spack/bin' in p:
                spack_root = p.replace('bin', '')
        spack_lib_path = join(spack_root, 'lib', 'spack')
        syspath.insert(0, spack_lib_path)
        spack_external_libs = join(spack_lib_path, 'external')
        syspath.insert(0, spack_external_libs)

    def setUp(self):
        rmtree(self.projectdir, ignore_errors=True)
        rmtree(self.machinedir, ignore_errors=True)
    
    def tearDown(self):
        rmtree(self.projectdir, ignore_errors=True)
        rmtree(self.machinedir, ignore_errors=True)

    def test_setup_spaces(self):
        self.assertFalse(isdir(self.projectdir))
        self.assertFalse(isdir(self.machinedir))
        setup_spaces(self.project, self.machine)
        filedir, filename = split(abspath(__file__))
        self.assertTrue(isdir(self.projectdir))
        self.assertTrue(isdir(self.machinedir))
        self.assertTrue(isdir(join(self.machinedir, 'licenses')))
        self.assertTrue(exists(join(self.machinedir,
                                    'licenses', 'license.lic')))

