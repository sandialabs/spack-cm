"""
Test generate.py
"""

import unittest
from src.core.generate import *
from os.path import split, abspath, dirname, join, exists
from os import environ, remove
import yaml
from shutil import copyfile

class test_GenerateYAMLs(unittest.TestCase):
    """
    Test YAML file generation from src.core.generate
    """
    @classmethod
    def setUpClass(cls):
        filedir, file = split(abspath(__file__))
        install_path = join(filedir, 'install_path')
        module_path = join(filedir, 'module_path')
        cls.project = 'tests'
        cls.machine = 'tests'
        cls.projectdir = join(dirname(dirname(filedir)),
                              'project', cls.project)
        copyfile(join(cls.projectdir, 'tests-compilers-manifest.yaml'),
                 join(cls.projectdir, 'tests-manifest.yaml'))
        environ['SPACK_CM_BASE_COMPILER'] = 'gcc@1.0.1'
        environ['SPACK_CM_PROJECT_NAME'] = cls.project
        environ['SPACK_CM_MACHINE_NAME'] = cls.machine
        environ['SPACK_CM_INSTALL_PATH'] = install_path
        environ['SPACK_CM_MODULEFILES_PATH'] = module_path
        environ['SPACK_CM_COMPILER_INSTALL_PATH'] = install_path + 'compiler/'
        environ['SPACK_CM_UTILITY_INSTALL_PATH'] = install_path + 'utility/'
        environ['SPACK_CM_TPL_INSTALL_PATH'] = install_path + 'tpl/'
        environ['SPACK_CM_BASE_PACKAGES_INSTALL_PATH'] = install_path + 'base-packages/'
        environ['SPACK_CM_LMOD_INSTALL_PATH'] = install_path + 'lmod/'
        with open(join(cls.projectdir, 'tests-manifest.yaml'), 'r') as f:
            contents = yaml.full_load(f)
        for key in contents:
            st = ', '
            environ[key] = st.join(contents[key])

    @classmethod
    def tearDownClass(cls):
        remove(join(cls.projectdir, 'tests-manifest.yaml'))
        for key in environ:
            if 'SEMS' in key:
                del environ[key]

    def test_base_packages(self):
        spack_base_package_yaml(self.project)
        self.assertTrue(exists(join(self.projectdir, 'base-packages-spack.yaml')))
        with open(join(self.projectdir, 'base-packages-spack.yaml'), 'r') as f:
            contents = yaml.full_load(f)
        self.assertIn('../../platform/tests/packages.yaml',
                      contents['spack']['include'])
        self.assertIn(environ['SPACK_CM_BASE_PACKAGES_INSTALL_PATH'],
                      contents['spack']['config']['install_tree']['root'])
        remove(join(self.projectdir, 'base-packages-spack.yaml'))

    def test_lmod(self):
        spack_lmod_yaml(self.project)
        self.assertTrue(exists(join(self.projectdir, 'lmod-spack.yaml')))
        with open(join(self.projectdir, 'lmod-spack.yaml'), 'r') as f:
            contents = yaml.full_load(f)
        self.assertIn('{}/packages.yaml'.format(environ['SPACK_CM_BASE_PACKAGES_INSTALL_PATH']),
                      contents['spack']['include'])
        self.assertIn(environ['SPACK_CM_LMOD_INSTALL_PATH'],
                      contents['spack']['config']['install_tree']['root'])
        remove(join(self.projectdir, 'lmod-spack.yaml'))

    def test_compilers(self):
        spack_compilers_yaml(self.project, False)
        self.assertTrue(exists(join(self.projectdir, 'compilers-spack.yaml')))
        with open(join(self.projectdir, 'compilers-spack.yaml'), 'r') as f:
            contents = yaml.full_load(f)
        self.assertIn('{}/packages.yaml'.format(environ['SPACK_CM_BASE_PACKAGES_INSTALL_PATH']),
                      contents['spack']['include'])
        self.assertIn(environ['SPACK_CM_COMPILER_INSTALL_PATH'],
                      contents['spack']['config']['install_tree']['root'])
        self.assertEqual([x or None for x in [environ['SPACK_CM_BASE_COMPILER']]],
                      [x for x in contents['spack']['definitions'][0]['core_compiler']])
        remove(join(self.projectdir, 'compilers-spack.yaml'))

    def test_utilities(self):
        spack_utilities_yaml(self.project, False)
        self.assertTrue(exists(join(self.projectdir, 'utilities-spack.yaml')))
        with open(join(self.projectdir, 'utilities-spack.yaml'), 'r') as f:
            contents = yaml.full_load(f)
        self.assertIn('{}/compilers.yaml'.format(environ['SPACK_CM_COMPILER_INSTALL_PATH']),
                      contents['spack']['include'])
        self.assertIn(environ['SPACK_CM_UTILITY_INSTALL_PATH'],
                      contents['spack']['config']['install_tree']['root'])
        self.assertIn(environ['SPACK_CM_UTILITY_COMPILER'],
                      contents['spack']['definitions'][0]['core_compiler'])
        remove(join(self.projectdir, 'utilities-spack.yaml'))

    def test_tpls_project_on(self):
        spack_tpl_yaml(self.project, True)
        self.assertTrue(exists(join(self.projectdir, 'tpl-spack.yaml')))
        with open(join(self.projectdir, 'tpl-spack.yaml'), 'r') as f:
            contents = yaml.full_load(f)
        self.assertIn('{}/packages.yaml'.format(environ['SPACK_CM_UTILITY_INSTALL_PATH']),
                      contents['spack']['include'])
        self.assertIn(environ['SPACK_CM_TPL_INSTALL_PATH'],
                      contents['spack']['config']['install_tree']['root'])
        self.assertIn('prefix_inspections',
                      contents['spack']['modules'])
        self.assertIn(self.project + '-{name}/{version}',
                      contents['spack']['modules']['lmod']['projections']['all'])
        remove(join(self.projectdir, 'tpl-spack.yaml'))

    def test_tpls_project_off(self):
        spack_tpl_yaml(self.project, False)
        with open(join(self.projectdir, 'tpl-spack.yaml'), 'r') as f:
            contents = yaml.full_load(f)
        self.assertIn('{name}/{version}',
                      contents['spack']['modules']['lmod']['projections']['all'])
        remove(join(self.projectdir, 'tpl-spack.yaml'))

    def test_tpls_no_mpi(self):
        environ['SPACK_CM_MPIS'] = ''
        spack_tpl_yaml(self.project, False)
        with open(join(self.projectdir, 'tpl-spack.yaml'), 'r') as f:
            contents = yaml.full_load(f)
        self.assertNotIn('$mpis',
                      contents['spack']['specs'][0]['matrix'][0])
        environ['SPACK_CM_MPIS'] = 'openmpi@4.0.5'
        remove(join(self.projectdir, 'tpl-spack.yaml'))

    def test_tpls_mpi_no_cuda(self):
        environ['SPACK_CM_MPIS'] = 'openmpi@4.0.5'
        spack_tpl_yaml(self.project, False)
        with open(join(self.projectdir, 'tpl-spack.yaml'), 'r') as f:
            contents = yaml.full_load(f)
        self.assertIn('$mpis',
                      contents['spack']['specs'][0]['matrix'][0])
        self.assertIn('$^mpis',
                      contents['spack']['specs'][1]['matrix'][2])
        remove(join(self.projectdir, 'tpl-spack.yaml'))

    def test_tpls_cudas(self):
        environ['SPACK_CM_CUDAS'] = 'cuda@11'
        spack_tpl_yaml(self.project, True)
        with open(join(self.projectdir, 'tpl-spack.yaml'), 'r') as f:
            contents = yaml.full_load(f)
        self.assertIn('cudas',
                      contents['spack']['definitions'][3])
        self.assertIn('$^cudas',
                      contents['spack']['specs'][1]['matrix'][2])
        self.assertIn('$cudas',
                      contents['spack']['specs'][0]['matrix'][0])
        environ['SPACK_CM_CUDAS'] = ''
        remove(join(self.projectdir, 'tpl-spack.yaml'))

    def test_exclude_odd_symbol(self):
        environ['SPACK_CM_EXCLUDE_COMBOS'] = '%gcc@10.1.0 ^openmpi@1.10.7, valgrind%gcc@4.8.5'
        spack_tpl_yaml(self.project, True)
        with open(join(self.projectdir, 'tpl-spack.yaml'), 'r') as f:
            contents = f.read()
        self.assertIn('"%gcc@10.1.0 ^openmpi@1.10.7"',
                      contents)
        with open(join(self.projectdir, 'tpl-spack.yaml'), 'r') as f:
            contents = yaml.full_load(f)
