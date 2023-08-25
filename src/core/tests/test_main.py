"""
Test main.py
"""

import unittest
from src.core.main import buildParser, main, MainException
from os.path import abspath, expanduser


class test_MainDriver(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser = buildParser()

    def test_setup_parser(self):
        setup = self.parser.parse_args(['setup', '-p', 'tests'])
        self.assertEqual(setup.command, 'setup')
        self.assertEqual(setup.althostname, None)
        self.assertEqual(setup.project, 'tests')

    def test_install_parser(self):
        install = self.parser.parse_args(['install', '-p', 'tests',
                                          '-r', '~/'])
        self.assertEqual(install.command, 'install')
        self.assertEqual(install.project, 'tests')
        self.assertEqual(install.althostname, None)
        self.assertEqual(install.root_path, abspath(expanduser('~/')))
        self.assertEqual(install.stage, 'all')
        self.assertFalse(install.debug)
        self.assertFalse(install.external)
        self.assertTrue(install.projmod)
        self.assertFalse(install.machine_path)
        self.assertFalse(install.spackdeps)
        install = self.parser.parse_args(['install', '-e', '-d',
                                          '--install-spack-deps',
                                          '--no-project-modules',
                                          '--add-machine-to-install-path',
                                          '--dry-run'])
        self.assertTrue(install.debug)
        self.assertTrue(install.external)
        self.assertFalse(install.projmod)
        self.assertTrue(install.spackdeps)
        self.assertTrue(install.machine_path)
        self.assertEqual(install.fake, '--fake')
        install = self.parser.parse_args(['install', '-s', 'tpl',
                                          '--spack', '0.16.0'])
        self.assertEqual(install.stage, 'tpl')
        self.assertEqual(install.fake, '')
        self.assertEqual(install.spackbranch, '0.16.0')

    def test_invalid_command(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args(['invalidcommand'])

    def test_unknown_commands(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args(['setup', '-s', 'tpl'])
            self.parser.parse_args(['install', '-t', 'typo'])

    def test_no_project(self):
        with self.assertRaises(MainException):
            arguments = self.parser.parse_args(['setup'])
            main(arguments)
        with self.assertRaises(MainException):
            arguments = self.parser.parse_args(['install'])
            main(arguments)

    def test_no_root_path(self):
        with self.assertRaises(MainException):
            arguments = self.parser.parse_args(['install', '-p', 'tests'])
            main(arguments)
