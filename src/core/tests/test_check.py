"""
Test check spack methods
"""

import unittest
from src.core.check import check_spack, CheckSpackException, check
from os import environ
import subprocess


class test_CheckSpack(unittest.TestCase):
    """
    Test check_spack method from src.core.check - pass and fail.
    """
    @classmethod
    def setUpClass(cls):
        cls.path = environ['PATH']
        cls.version = 'v0.16.2'

    def test_check_spack_not_on_path(self):
        environ['PATH'] = '/usr/bin'
        with self.assertRaises(CheckSpackException) as e:
            check_spack(self.version)
        self.assertTrue('Spack not found on PATH' in str(e.exception))

    def test_check_spack_on_path(self):
        environ['PATH'] = self.path
        check_spack(self.version)

    def test_change_spack_version(self):
        check_spack(self.version)
        spack_version = subprocess.Popen(['spack', '--version'],
                                         stdout=subprocess.PIPE).communicate()[0].strip().decode('utf-8')
        self.assertEqual(self.version, 'v' + spack_version)
        old_version = 'v0.16.0'
        check_spack(old_version)
        spack_version = subprocess.Popen(['spack', '--version'],
                                         stdout=subprocess.PIPE).communicate()[0].strip().decode('utf-8')
        self.assertEqual(old_version, 'v' + spack_version)

    def test_use_develop_branch(self):
        branch = 'develop'
        check_spack(branch)
        spack_branch = subprocess.Popen(['git', 'status'], stdout=subprocess.PIPE).communicate()[0].decode('utf-8').split('\n')[0].split(' ')[-1]
        self.assertEqual(branch, spack_branch)
        check_spack(self.version)

    def test_check_load_main(self):
        environ['PATH'] = self.path
        check_spack(self.version)
        import spack.main

    def test_full_check(self):
        check(self.version, False)
