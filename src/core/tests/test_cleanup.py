"""
Test the Spack cleanup routines.
"""

import unittest
from src.core.cleanup import (spack_cleanup, spack_compiler_find,
                              spack_external_find, spack_license_cleanup)
import os
from os.path import dirname
import shutil
import subprocess
from sys import path as syspath

class test_SpackCleanup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spack_root = subprocess.run(['which', 'spack'], stdout=subprocess.PIPE)
        spack_root = dirname(dirname(spack_root.stdout.decode('utf-8').strip()))
        spack_lib_path = os.path.join(spack_root, "lib", "spack")
        syspath.insert(0, spack_lib_path)
        spack_external_libs = os.path.join(spack_lib_path, "external")
        syspath.insert(0, spack_external_libs)
        if not os.path.isdir(os.path.expanduser('~/.spack')):
            os.mkdir(os.path.expanduser('~/.spack'))

    @classmethod
    def tearDownClass(cls):
        if os.path.isdir(os.path.expanduser('~/.spack')):
            shutil.rmtree(os.path.expanduser('~/.spack'))
        if os.path.isdir(os.path.expanduser('~/bogus/not/here/')):
            shutil.rmtree(os.path.expanduser('~/bogus/not/here/'))

    def test_spack_cleanup(self):
        spack_cleanup('~/bogus/not/here')
        self.assertFalse(os.path.isdir(os.path.expanduser('~/.spack')))
        os.makedirs(os.path.expanduser('~/bogus/not/here/.spack-env'))
        with open(os.path.expanduser('~/bogus/not/here/spack.lock'), 'w') as file:
            file.write('This is not a file you want.')
        spack_cleanup(os.path.expanduser('~/bogus/not/here'))
        self.assertFalse(os.path.isdir(
            os.path.expanduser('~/bogus/not/here/.spack-env')))
        self.assertFalse(os.path.exists(
            os.path.expanduser('~/bogus/not/here/spack.lock')))

    def test_compiler_find(self):
        spack_compiler_find()
        self.assertTrue(os.path.isdir(os.path.expanduser('~/.spack')))

    def test_external_find(self):
        spack_external_find()
        self.assertTrue(os.path.exists(os.path.expanduser('~/.spack/packages.yaml')))

    def test_license_cleanup(self):
        if not os.path.isdir(os.path.join(
                os.environ['SPACK_ROOT'], 'etc/spack/licenses/intel')):
            os.makedirs(os.path.join(os.path.join(
                os.environ['SPACK_ROOT'], 'etc/spack/licenses/intel')))
        spack_license_cleanup()
        self.assertFalse(os.path.isdir(
            os.path.join(os.environ['SPACK_ROOT'], 'etc/spack/licenses/intel')))

