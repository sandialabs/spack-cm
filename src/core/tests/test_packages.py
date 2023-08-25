"""
Test packages.py
"""

import unittest
import yaml
from src.core.packages import generate_packages_yaml
import os

class test_Packages(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        filedir, filename = os.path.split(os.path.abspath(__file__))
        cls.install_path = os.path.join(filedir, 'install_path', 'utility')

        if os.path.exists(os.path.join(cls.install_path, 'packages.yaml')):
            os.remove(os.path.join(cls.install_path, 'packages.yaml'))

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(os.path.join(cls.install_path, 'packages.yaml')):
            os.remove(os.path.join(cls.install_path, 'packages.yaml'))
            pass

    def test_install_path_exists(self):
        self.assertTrue(os.path.isdir(self.install_path))

    def test_packages_yaml_created(self):
        generate_packages_yaml(self.install_path)
        self.assertTrue(os.path.exists(os.path.join(
            self.install_path, 'packages.yaml')))

    def test_packages_yaml_contents(self):
        generate_packages_yaml(self.install_path)
        with open(self.install_path+"/packages.yaml") as f:
            file_contents=yaml.full_load(f)
            print(file_contents['packages'])
            self.assertIn('texlive', file_contents['packages'].keys())
            self.assertIn('externals', file_contents['packages']['texlive'])
            self.assertIn('prefix', file_contents['packages']['texlive']['externals'][0])
            self.assertIn('/projects/sems/install/rhel7-x86_64/sems-beta/utility/texlive',
                          file_contents['packages']['texlive']['externals'][0]['prefix'])
