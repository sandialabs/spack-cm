"""
Test utilities.py
"""

import pytest
import re
import subprocess
import unittest
from filecmp import cmp
from os import environ, remove
from os.path import split, abspath, dirname, join, exists, isdir
from pathlib import Path
from shutil import rmtree, copyfile
from socket import gethostname
from src.core.utilities import *


class test_Utilities(unittest.TestCase):
    """
    Test utilities method from src.core.utilities
    """
    @classmethod
    def setUpClass(cls):
        cls.project = 'tests'
        cls.machine = 'tests'
        cls.filedir, cls.filename = split(abspath(__file__))
        cls.projectdir = join(dirname(dirname(cls.filedir)),
                              'project', cls.project)
        copyfile(join(cls.projectdir, 'tests-utilities-manifest.yaml'),
                 join(cls.projectdir, 'tests-manifest.yaml'))
        cls.repo_root_dir = dirname(dirname(dirname(cls.filedir)))
        cls.lmod_install_dir = join(cls.repo_root_dir,
                                    "src/core/tests/install_path/lmod")
        cls.explicit_install_dir = None
        cls.explicit_module_dir = None

        cls.module_install_dir = "/path/to/where/modules/are/installed"
        cls.module_init_install_path = join(cls.projectdir,
                                            'module-init-scripts')
        cls.module_init_file_name = cls.project + "-modules-" + cls.machine + "-init.sh"

        if exists(join(cls.module_init_install_path, cls.module_init_file_name)):
            remove(join(cls.module_init_install_path, cls.module_init_file_name))


    @classmethod
    def tearDownClass(cls):
        remove(join(cls.projectdir, 'tests-manifest.yaml'))
        if exists(join(cls.module_init_install_path, cls.module_init_file_name)):
            remove(join(cls.module_init_install_path,
                        cls.module_init_file_name))


    def test_dir_path(self):
        message = 'path does not expand correctly'
        self.assertEqual(dir_path(self.projectdir), self.projectdir, message)
        home = str(Path.home())
        self.assertEqual(dir_path('~'), home, message)
        bad_path = '/this/is/not/a/path'
        with self.assertRaises(argparse.ArgumentTypeError) as e:
            dir_path(bad_path)


    def test_get_hostname(self):
        message = 'OS does not match hostname.'
        hostname = gethostname()
        if hostname == 'somac1014tpl01':
            self.assertEqual(get_hostname(), 'Darwin10.14-x86_64', message)
        elif hostname == 'somac1015tpl01':
            self.assertEqual(get_hostname(), 'Darwin10.15-x86_64', message)
        elif hostname == 'sems-son-rhel7-tpl-01':
            self.assertEqual(get_hostname(), 'rhel7-x86_64', message)
        elif hostname == 'sems-son-rhel8-tpl-01':
            self.assertEqual(get_hostname(), 'rhel8_x86_64', message)
        elif hostname == 'chama' or hostname == 'skybridge':
            self.assertEqual(get_hostname(), 'toss3', message)
        else:
            self.assertEqual(hostname, gethostname(), message)


    @pytest.mark.long
    def test_spack_dependencies(self):
        try:
            spack_dependencies()
            pass
        except UtilityException:
            self.fail('spack_dependencies() threw UtilityException')
        packages = ['curl', 'patch', 'bzip2']
        for package in packages:
            self.assertTrue(subprocess.run('spack find -p -d {}'.format(package),
                                           shell=True, stdout=subprocess.PIPE,
                                           universal_newlines=True))


    def test_env_var_list(self):
        message = 'Converting env var failed.'
        name = 'test_var'
        environ[name] = 'something'
        self.assertEqual(env_var_list(name), [environ[name]], message)
        environ[name] = 'something, this, whatever'
        self.assertEqual(env_var_list(name),
                         'something, this, whatever'.split(', '), message)
        with self.assertRaises(UtilityException) as e:
            env_var_list('not_in_the_env')


    def test_generate_file(self):
        message = 'Generate file failed'
        filename = join(self.projectdir, 'tests_generate.yaml')
        contents = 'These are definitely contents.'
        generate_file(filename, contents)
        with open(filename, 'r') as f:
            data = f.read()
        self.assertEqual(data, contents + '\n...\n', message)
        remove(filename)


    def test_check_project_yaml_files(self):
        message = 'Project yaml check Failed'
        export_env_vars(self.project, self.machine, self.projectdir, False,
                        self.explicit_install_dir, self.explicit_module_dir)
        check_project_yaml_files()
        dir_yaml_path = [('compiler/', 'compilers.yaml'),
                         ('utility/', 'packages.yaml'),
                         ('base-packages/', 'packages.yaml')]
        for dir_path, yaml_file in dir_yaml_path:
            path = join(environ['SPACK_CM_INSTALL_PATH'], dir_path)
            self.assertTrue(isdir(path), message)
            file = join(path, yaml_file)
            self.assertTrue(isfile(file))
            rmtree(path)
        rmtree(environ['SPACK_CM_INSTALL_PATH'])

    def test_replace_single_quotes(self):
        message = 'Replacing single quotes failed'
        text_with_single_quotes = '\'this\' is the \"sort\" of \'quoted\' text we \"need to\" \'fix\'?'
        text_without_quotes = 'this is the \"sort\" of quoted text we \"need to\" fix\'\''

        filename = join(self.projectdir, 'test_quotes.yaml')
        with open(filename, 'w') as f:
            f.write(text_with_single_quotes)
        replace_single_quotes(filename)
        with open(filename, 'r') as f:
            data = f.read()
        self.assertEqual(data, text_without_quotes, message)
        remove(filename)


    def test_export_env_vars(self):
        message = 'Export environment variables failed'
        export_env_vars(self.project, self.machine, self.projectdir, False,
                        self.explicit_install_dir, self.explicit_module_dir)
        self.assertEqual(environ['SPACK_CM_PROJECT_NAME'], self.project, message)
        self.assertEqual(environ['SPACK_CM_MACHINE_NAME'], self.machine, message)
        self.assertEqual(
            environ['SPACK_CM_INSTALL_PATH'],
            join(self.projectdir, 'install', self.project) + '/', message)
        gcc_version = subprocess.run('gcc --version',
                                     shell=True,
                                     stdout=subprocess.PIPE,
                                     universal_newlines=True)
        for base_compiler in re.split('@|-', environ['SPACK_CM_BASE_COMPILER']):
            self.assertIn(base_compiler, gcc_version.stdout, message)
        self.assertEqual(environ['SPACK_CM_UTILITY_COMPILER'], 'gcc@7.3.0', message)
        self.assertEqual(environ['SPACK_CM_MPIS'], 'openmpi@4.0.5', message)
        self.assertEqual(environ['SPACK_CM_COMPILERS'], '', message)
        for base_compiler in re.split('@|-', environ['SPACK_CM_EXTERNAL_COMPILERS']):
            self.assertIn(base_compiler, gcc_version.stdout, message)
        for key in environ.keys():
            if 'SEMS' in key:
                del environ[key]


    def test_copy_spack_yaml(self):
        message = 'Copy Spack yaml failed'
        filename = 'tests-manifest.yaml'
        filecopy = join(self.projectdir, 'spack.yaml')

        copy_spack_yaml(self.project, filename)
        self.assertTrue(cmp(join(self.projectdir, filename),
                            filecopy, shallow=False), message)
        remove(filecopy)


    def test_module_init_install_path_exists(self):
        self.assertTrue(isdir(self.module_init_install_path))


    def test_module_init_created(self):
        generate_module_init_script(self.project, self.machine,
                                    self.lmod_install_dir,
                                    self.module_install_dir)
        self.assertTrue(exists(join(self.module_init_install_path,
                                    self.module_init_file_name)))


    def test_module_init_contents(self):
        generate_module_init_script(self.project, self.machine,
                                    self.lmod_install_dir,
                                    self.module_install_dir)
        with open(self.module_init_install_path + "/" + self.module_init_file_name) as f:
            file_contents=f.read()
        self.assertIn("src/core/tests/install_path/lmod/5.6.7/gcc/1.0.1/whatever/directory/leads/to/init/files/bash",
                      file_contents)
        self.assertIn("module use /path/to/where/modules/are/installed/Core",
                      file_contents)
