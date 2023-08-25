"""
Generate necessary Spack YAML files
"""

from src.core.utilities import (env_var_list, replace_single_quotes,
                                generate_file, export_env_vars,
                                pcolors)
from os.path import split, abspath, dirname
from os import environ
import logging
logger = logging.getLogger(__name__)


class GenerateException(Exception):
    """Catch all generation exceptions"""
    pass


def spack_base_package_yaml(project):
    """
    Generate base packages YAML file.

    Parameters
    ----------
    project : String
        Project for which to generate this file.

    """
    SPACK_CM_BASE_PACKAGES = env_var_list('SPACK_CM_BASE_PACKAGES')
    SPACK_CM_BASE_COMPILER = env_var_list('SPACK_CM_BASE_COMPILER')
    INSTALL_PATH = environ['SPACK_CM_BASE_PACKAGES_INSTALL_PATH']
    MACHINE = environ['SPACK_CM_MACHINE_NAME']
    PROJECT = environ['SPACK_CM_PROJECT_NAME']
    MODULE_ROOT = environ['SPACK_CM_MODULEFILES_PATH']
    contents = {'spack' :
                {'include' : ['../../project/{}/repos.yaml'.format(PROJECT),
                              '../../project/{}/packages.yaml'.format(PROJECT),
                              '../../platform/{}/packages.yaml'.format(MACHINE),
                              '../../platform/{}/mirrors.yaml'.format(MACHINE),
                              '../../platform/{}/compilers.yaml'.format(MACHINE)],
                 'definitions' : [{'core_compiler' : SPACK_CM_BASE_COMPILER},
                                  {'base_packages' : SPACK_CM_BASE_PACKAGES}],
                 'specs' : [{'matrix' : [ '[$base_packages]' , '[$%core_compiler]' ] }],
                 'config' : {'install_tree' :
                             {'root' : INSTALL_PATH,
                              'projections': {'all': '"{name}/{version}/{compiler.name}/{compiler.version}/{hash:7}"'}},
                                 'module_roots' : {'lmod': '{}'.format(MODULE_ROOT)},
                                 'install_missing_compilers' : True },
                     'view' : False}}
    filedir, file = split(abspath(__file__))
    projectdir = dirname(filedir) + '/project/{}'.format(project)
    filename = projectdir + '/base-packages-spack.yaml'
    generate_file(filename, contents)
    replace_single_quotes(filename)


def spack_lmod_yaml(project):
    """
    Generate LMOD YAML file.

    Parameters
    ----------
    project : String
        Project for which to generate this file.

    """
    BP_INSTALL_PATH = environ['SPACK_CM_BASE_PACKAGES_INSTALL_PATH']
    INSTALL_PATH = environ['SPACK_CM_LMOD_INSTALL_PATH']
    MACHINE = environ['SPACK_CM_MACHINE_NAME']
    PROJECT = environ['SPACK_CM_PROJECT_NAME']
    MODULE_ROOT = environ['SPACK_CM_MODULEFILES_PATH']
    contents = {'spack' :
                {'include' : ['{}/packages.yaml'.format(BP_INSTALL_PATH),
                              '../../project/{}/repos.yaml'.format(PROJECT),
                              '../../project/{}/packages.yaml'.format(PROJECT),
                              '../../platform/{}/packages.yaml'.format(MACHINE),
                              '../../platform/{}/mirrors.yaml'.format(MACHINE),
                              '../../platform/{}/compilers.yaml'.format(MACHINE)],
                 'specs' : ['lmod'],
                 'config' : {'install_tree' :
                             {'root' : INSTALL_PATH,
                              'projections': {'all': '{name}/{version}/{compiler.name}/{compiler.version}/{hash:7}'}},
                                 'module_roots' : {'lmod': '{}'.format(MODULE_ROOT)},
                                 'install_missing_compilers' : False},
                     'view' : False}}
    filedir, file = split(abspath(__file__))
    projectdir = dirname(filedir) + '/project/{}'.format(project)
    filename = projectdir + '/lmod-spack.yaml'
    generate_file(filename, contents)


def spack_compilers_yaml(project, projmod):
    """
    Generate compilers YAML file.

    Parameters
    ----------
    project : String
        Project for which to generate this file.

    """
    BP_INSTALL_PATH = environ['SPACK_CM_BASE_PACKAGES_INSTALL_PATH']
    SPACK_CM_BASE_COMPILER = environ['SPACK_CM_BASE_COMPILER']
    SPACK_CM_COMPILERS = env_var_list('SPACK_CM_COMPILERS')
    INSTALL_PATH = environ['SPACK_CM_COMPILER_INSTALL_PATH']
    MACHINE = environ['SPACK_CM_MACHINE_NAME']
    PROJECT = environ['SPACK_CM_PROJECT_NAME']
    MODULE_ROOT = environ['SPACK_CM_MODULEFILES_PATH']
    contents = {'spack' :
                {'include' : ['{}/packages.yaml'.format(BP_INSTALL_PATH),
                              '../../project/{}/repos.yaml'.format(PROJECT),
                              '../../project/{}/packages.yaml'.format(PROJECT),
                              '../../platform/{}/packages.yaml'.format(MACHINE),
                              '../../platform/{}/mirrors.yaml'.format(MACHINE),
                              '../../platform/{}/compilers.yaml'.format(MACHINE)],
                 'definitions' : [{'core_compiler' : [SPACK_CM_BASE_COMPILER]},
                                  {'compilers_to_build' : SPACK_CM_COMPILERS}],
                 'specs' : [{'matrix' : [ '[$compilers_to_build]' , '[$%core_compiler]' ] }],
                 'config' : {'install_tree' :
                             {'root' : INSTALL_PATH,
                              'projections': {'all': '"{name}/{version}/{compiler.name}/{compiler.version}/{hash:7}"'}},
                                 'module_roots' : {'lmod': '{}'.format(MODULE_ROOT)},
                                 'install_missing_compilers' : False },
                  'view' : False,
                  'modules': {'enable' : ['lmod'],
                             'prefix_inspections' : {'bin' : ['PATH'],
                                                     'man' : ['MANPATH'],
                                                     'share/man' : ['ACLOCAL_PATH'],
                                                     'lib' : ['LIBRARY_PATH', 'LD_LIBRARY_PATH'],
                                                     'lib64' : ['LIBRARY_PATH', 'LD_LIBRARY_PATH'],
                                                     'include' : ['CPATH', 'INCLUDE'],
                                                     'lib/pkgconfig' : ['PKG_CONFIG_PATH'],
                                                     'lib64/pkgconfig' : ['PKG_CONFIG_PATH'],
                                                     'share/pkgconfig' : ['PKG_CONFIG_PATH'],
                                                     '?' : ['CMAKE_PREFIX_PATH']},
                             'lmod' : {'hash_length' : 0,
                                       'core_specs' : SPACK_CM_COMPILERS + [SPACK_CM_BASE_COMPILER],
                                       'whitelist' : '{}'.format(SPACK_CM_COMPILERS + [SPACK_CM_BASE_COMPILER]),
                                       'blacklist_implicits' : True,
                                       'all' : {'conflict': ['"{name}"'],
                                                'environment': {'set': {'"{name}_ROOT"' : '"{prefix}"',
                                                                        '"{name}_VERSION"' : '"{version}"',
                                                                        '"{name}_BIN"' : '"{prefix.bin}"',
                                                                        '"{name}_INC"' : '"{prefix.include}"',
                                                                        '"{name}_LIB"' : '"{prefix.lib}"'}}},
                                       'projections' : {'all' : ''},
                                       'verbose' : True}}
                      }}
    if projmod:
        contents['spack']['modules']['lmod']['projections']['all'] = '"{}-{{name}}/{{version}}"'.format(project)
    else:
        contents['spack']['modules']['lmod']['projections']['all'] = '"{name}/{version}"'
    filedir, file = split(abspath(__file__))
    projectdir = dirname(filedir) + '/project/{}'.format(project)
    filename = projectdir + '/compilers-spack.yaml'
    generate_file(filename, contents)
    replace_single_quotes(filename)


def spack_utilities_yaml(project, projmod):
    """
    Generate utilities YAML file.

    Parameters
    ----------
    project : String
        Project for which to generate this file.

    """
    BP_INSTALL_PATH = environ['SPACK_CM_BASE_PACKAGES_INSTALL_PATH']
    C_INSTALL_PATH = environ['SPACK_CM_COMPILER_INSTALL_PATH']
    SPACK_CM_COMPILERS = env_var_list('SPACK_CM_COMPILERS')
    SPACK_CM_UTILITIES = env_var_list('SPACK_CM_UTILITIES')
    SPACK_CM_UTILITY_COMPILER = environ['SPACK_CM_UTILITY_COMPILER']
    INSTALL_PATH = environ['SPACK_CM_UTILITY_INSTALL_PATH']
    MACHINE = environ['SPACK_CM_MACHINE_NAME']
    PROJECT = environ['SPACK_CM_PROJECT_NAME']
    MODULE_ROOT = environ['SPACK_CM_MODULEFILES_PATH']
    contents = {'spack' :
                {'include' : ['{}/packages.yaml'.format(BP_INSTALL_PATH),
                              '../../project/{}/repos.yaml'.format(PROJECT),
                              '../../project/{}/packages.yaml'.format(PROJECT),
                              '../../platform/{}/packages.yaml'.format(MACHINE),
                              '../../platform/{}/mirrors.yaml'.format(MACHINE),
                              '../../platform/{}/compilers.yaml'.format(MACHINE)],
                 'definitions' : [{'core_compiler' : [SPACK_CM_UTILITY_COMPILER]},
                                  {'utility_packages' : SPACK_CM_UTILITIES}],
                 'specs' : [{'matrix' : [ '[$utility_packages]' , '[$%core_compiler]' ] }],
                 'config' : {'install_tree' :
                             {'root' : INSTALL_PATH,
                              'projections': {'^mpi': '"{name}/{version}/{compiler.name}/{compiler.version}/{^mpi.name}/{^mpi.version}/{hash:7}"',
                                              'all': '"{name}/{version}/{compiler.name}/{compiler.version}/{hash:7}"'}},
                                 'module_roots' : {'lmod': '{}'.format(MODULE_ROOT)},
                                 'install_missing_compilers' : False },
                 'view' : False,
                  'modules': {'enable' : ['lmod'],
                             'prefix_inspections' : {'bin' : ['PATH'],
                                                     'man' : ['MANPATH'],
                                                     'share/man' : ['ACLOCAL_PATH'],
                                                     'lib' : ['LIBRARY_PATH', 'LD_LIBRARY_PATH'],
                                                     'lib64' : ['LIBRARY_PATH', 'LD_LIBRARY_PATH'],
                                                     'include' : ['CPATH', 'INCLUDE'],
                                                     'lib/pkgconfig' : ['PKG_CONFIG_PATH'],
                                                     'lib64/pkgconfig' : ['PKG_CONFIG_PATH'],
                                                     'share/pkgconfig' : ['PKG_CONFIG_PATH'],
                                                     '?' : ['CMAKE_PREFIX_PATH']},
                              'lmod' : {'hash_length' : 0,
                                       'core_compilers' : [SPACK_CM_UTILITY_COMPILER],
                                       'core_specs' : SPACK_CM_UTILITIES ,
                                       'whitelist' : '{}'.format(SPACK_CM_UTILITIES),
                                       'blacklist_implicits' : True,
                                       'all' : {'conflict': ['"{name}"'],
                                                'environment': {'set': {'"{name}_ROOT"' : '"{prefix}"',
                                                                        '"{name}_VERSION"' : '"{version}"',
                                                                        '"{name}_BIN"' : '"{prefix.bin}"',
                                                                        '"{name}_INC"' : '"{prefix.include}"',
                                                                        '"{name}_LIB"' : '"{prefix.lib}"'}}},
                                       'projections' : {'all' : ''},
                                       'verbose' : True}}
                      }}
    if SPACK_CM_COMPILERS != ['']:
        contents['spack']['include'].insert(1, '{}/compilers.yaml'.format(C_INSTALL_PATH))
    if projmod:
        contents['spack']['modules']['lmod']['projections']['all'] = '"{}-{{name}}/{{version}}"'.format(project)
    else:
        contents['spack']['modules']['lmod']['projections']['all'] = '"{name}/{version}"'
    filedir, file = split(abspath(__file__))
    projectdir = dirname(filedir) + '/project/{}'.format(project)
    filename = projectdir + '/utilities-spack.yaml'
    generate_file(filename, contents)
    replace_single_quotes(filename)


def spack_tpl_yaml(project, projmod):
    """
    Generate TPL YAML file.

    Parameters
    ----------
    project : String
        Project for which to generate this file.

    """
    INSTALL_PATH = environ['SPACK_CM_TPL_INSTALL_PATH']
    BP_INSTALL_PATH = environ['SPACK_CM_BASE_PACKAGES_INSTALL_PATH']
    C_INSTALL_PATH = environ['SPACK_CM_COMPILER_INSTALL_PATH']
    U_INSTALL_PATH = environ['SPACK_CM_UTILITY_INSTALL_PATH']
    SPACK_CM_UTILITY_COMPILER = environ['SPACK_CM_UTILITY_COMPILER']
    SPACK_CM_COMPILERS = env_var_list('SPACK_CM_COMPILERS')
    SPACK_CM_EXTERNAL_COMPILERS = env_var_list('SPACK_CM_EXTERNAL_COMPILERS')
    COMPILERS = [c for c in SPACK_CM_COMPILERS + SPACK_CM_EXTERNAL_COMPILERS if c]
    SPACK_CM_MPIS = env_var_list('SPACK_CM_MPIS')
    SPACK_CM_EXTERNAL_MPIS = env_var_list('SPACK_CM_EXTERNAL_MPIS')
    MPIS = [c for c in SPACK_CM_MPIS + SPACK_CM_EXTERNAL_MPIS if c]
    SPACK_CM_CUDAS = env_var_list('SPACK_CM_CUDAS')
    SPACK_CM_EXTERNAL_CUDAS = env_var_list('SPACK_CM_EXTERNAL_CUDAS')
    CUDAS = [c for c in SPACK_CM_CUDAS + SPACK_CM_EXTERNAL_CUDAS if c]
    SPACK_CM_TPLS = env_var_list('SPACK_CM_TPLS')
    MACHINE = environ['SPACK_CM_MACHINE_NAME']
    PROJECT = environ['SPACK_CM_PROJECT_NAME']
    MODULE_ROOT = environ['SPACK_CM_MODULEFILES_PATH']
    EXCLUDE = env_var_list('SPACK_CM_EXCLUDE_COMBOS')
    contents = {'spack' :
                {'include' : ['{}/packages.yaml'.format(BP_INSTALL_PATH),
                              '{}/packages.yaml'.format(U_INSTALL_PATH),
                              '../../project/{}/packages.yaml'.format(PROJECT),
                              '../../project/{}/repos.yaml'.format(PROJECT),
                              '../../platform/{}/packages.yaml'.format(MACHINE),
                              '../../platform/{}/mirrors.yaml'.format(MACHINE),
                              '../../platform/{}/compilers.yaml'.format(MACHINE)],
                 'definitions' : [{'compilers' : COMPILERS},
                                  {'packages' : SPACK_CM_TPLS}],
                 'specs' : [{'matrix' : [ '[$packages]' , '[$%compilers]']}],
                 'config' : {'install_tree' :
                             {'root' : INSTALL_PATH,
                              'projections': {'^mpi': '"{name}/{version}/{compiler.name}/{compiler.version}/{^mpi.name}/{^mpi.version}/{hash:7}"',
                                              'all': '"{name}/{version}/{compiler.name}/{compiler.version}/base/{hash:7}"'}},
                                 'module_roots' : {'lmod': '{}'.format(MODULE_ROOT)},
                                 'install_missing_compilers' : False },
                 'view' : False,
                 'modules': {'enable' : ['lmod'],
                             'prefix_inspections' : {'bin' : ['PATH'],
                                                     'man' : ['MANPATH'],
                                                     'share/man' : ['ACLOCAL_PATH'],
                                                     'lib' : ['LIBRARY_PATH', 'LD_LIBRARY_PATH'],
                                                     'lib64' : ['LIBRARY_PATH', 'LD_LIBRARY_PATH'],
                                                     'include' : ['CPATH', 'INCLUDE'],
                                                     'lib/pkgconfig' : ['PKG_CONFIG_PATH'],
                                                     'lib64/pkgconfig' : ['PKG_CONFIG_PATH'],
                                                     'share/pkgconfig' : ['PKG_CONFIG_PATH'],
                                                     '?' : ['CMAKE_PREFIX_PATH']},
                             'lmod' : {'core_compilers' : [SPACK_CM_UTILITY_COMPILER],
                                       'core_specs' : COMPILERS,
                                       'hierarchy' : ['mpi'],
                                       'hash_length' : 0,
                                       'whitelist' : SPACK_CM_TPLS + COMPILERS,
                                       'blacklist' : ['lmod'],
                                       'blacklist_implicits' : True,
                                       'all' : {'conflict': ['"{name}"'],
                                                'environment': {'set': {'"{name}_ROOT"' : '"{prefix}"',
                                                                        '"{name}_VERSION"' : '"{version}"',
                                                                        '"{name}_BIN"' : '"{prefix.bin}"',
                                                                        '"{name}_INC"' : '"{prefix.include}"',
                                                                        '"{name}_LIB"' : '"{prefix.lib}"'}}},
                                       'projections' : {'all' : ''},
                                       'verbose' : True}}}}
    if SPACK_CM_COMPILERS != ['']:
        contents['spack']['include'].insert(2, '{}/compilers.yaml'.format(C_INSTALL_PATH))
    if MPIS:
        contents['spack']['definitions'].append({'mpis' : MPIS})
        contents['spack']['specs'].append(contents['spack']['specs'][0])
        contents['spack']['specs'][0] = {'matrix' : [ '[$mpis]' , '[$%compilers]']}
        contents['spack']['specs'][1]['matrix'].append('[$^mpis]')
        contents['spack']['modules']['lmod']['whitelist'] += MPIS
    if CUDAS:
        contents['spack']['definitions'].append({'cudas' : CUDAS})
        contents['spack']['specs'].insert(0, {'matrix' : [ '[$cudas]' , '[$%compilers]']})
        contents['spack']['specs'][1]['matrix'].append('[$^cudas]')
        contents['spack']['specs'][2]['matrix'].append('[$^cudas]')
        contents['spack']['modules']['lmod']['whitelist'] += CUDAS
    if EXCLUDE != ['']:
        i = 0
        # Items cannot start with %, which may happen in the EXCLUDE section
        # Turning them into strings with quotes to avoid this
        EXCLUDE = ['"' + item + '"' for item in EXCLUDE]
        while i < len(contents['spack']['specs']):
            contents['spack']['specs'][i]['exclude'] = EXCLUDE
            i += 1
    if projmod:
        contents['spack']['modules']['lmod']['projections']['all'] = '"{}-{{name}}/{{version}}"'.format(project)
    else:
        contents['spack']['modules']['lmod']['projections']['all'] = '"{name}/{version}"'
    filedir, file = split(abspath(__file__))
    projectdir = dirname(filedir) + '/project/{}'.format(project)
    filename = projectdir + '/tpl-spack.yaml'
    generate_file(filename, contents)
    replace_single_quotes(filename)

def spack_single_stack_yaml(project, projmod, single_stack_compiler=None, single_stack_mpi=None, single_stack_cuda=None):
    """
    Generate TPL YAML file.

    Parameters
    ----------
    project : String
        Project for which to generate this file.

    """
    INSTALL_PATH = environ['SPACK_CM_TPL_INSTALL_PATH']
    BP_INSTALL_PATH = environ['SPACK_CM_BASE_PACKAGES_INSTALL_PATH']
    C_INSTALL_PATH = environ['SPACK_CM_COMPILER_INSTALL_PATH']
    U_INSTALL_PATH = environ['SPACK_CM_UTILITY_INSTALL_PATH']
    SPACK_CM_UTILITIES = env_var_list('SPACK_CM_UTILITIES')
    SPACK_CM_COMPILERS = env_var_list('SPACK_CM_COMPILERS')
    SPACK_CM_EXTERNAL_COMPILERS = env_var_list('SPACK_CM_EXTERNAL_COMPILERS')
    COMPILERS = [c for c in SPACK_CM_COMPILERS + SPACK_CM_EXTERNAL_COMPILERS if c]
    SPACK_CM_TPLS = env_var_list('SPACK_CM_TPLS')
    MACHINE = environ['SPACK_CM_MACHINE_NAME']
    PROJECT = environ['SPACK_CM_PROJECT_NAME']
    MODULE_ROOT = environ['SPACK_CM_MODULEFILES_PATH']
    SPACK_CM_TPLS.extend(SPACK_CM_UTILITIES)
    if single_stack_mpi:
        SPACK_CM_TPLS.append(single_stack_mpi)
    if single_stack_cuda:
        SPACK_CM_TPLS.append(single_stack_cuda)
    contents = {'spack' :
                {'include' : ['{}/packages.yaml'.format(BP_INSTALL_PATH),
                              '{}/packages.yaml'.format(U_INSTALL_PATH),
                              '../../project/{}/repos.yaml'.format(PROJECT),
                              '../../platform/{}/packages.yaml'.format(MACHINE),
                              '../../platform/{}/mirrors.yaml'.format(MACHINE),
                              '../../platform/{}/compilers.yaml'.format(MACHINE)],
                 'definitions' : [{'compiler' : [single_stack_compiler]},
                                  {'packages' : SPACK_CM_TPLS}],
                 'concretization' : 'together',
                 'specs' : [{'matrix' : [ '[$packages]' , '[$%compiler]']}],
                 'config' : {'install_tree' :
                             {'root' : INSTALL_PATH,
                              'projections': {'^mpi': '"{name}/{version}/{compiler.name}/{compiler.version}/{^mpi.name}/{^mpi.version}/{hash:7}"',
                                              'all': '"{name}/{version}/{compiler.name}/{compiler.version}/base/{hash:7}"'}},
                                 'module_roots' : {'lmod': '{}'.format(MODULE_ROOT)},
                                 'install_missing_compilers' : False },
                 'view' : False,
                 'modules': {'enable' : ['lmod'],
                             'prefix_inspections' : {'bin' : ['PATH'],
                                                     'man' : ['MANPATH'],
                                                     'share/man' : ['ACLOCAL_PATH'],
                                                     'lib' : ['LIBRARY_PATH', 'LD_LIBRARY_PATH'],
                                                     'lib64' : ['LIBRARY_PATH', 'LD_LIBRARY_PATH'],
                                                     'include' : ['CPATH', 'INCLUDE'],
                                                     'lib/pkgconfig' : ['PKG_CONFIG_PATH'],
                                                     'lib64/pkgconfig' : ['PKG_CONFIG_PATH'],
                                                     'share/pkgconfig' : ['PKG_CONFIG_PATH'],
                                                     '?' : ['CMAKE_PREFIX_PATH']},
                             'lmod' : {'hierarchy' : ['mpi'],
                                       'hash_length' : 0,
                                       'whitelist' : SPACK_CM_TPLS,
                                       'blacklist' : ['lmod'],
                                       'blacklist_implicits' : True,
                                       'all' : {'conflict': ['"{name}"'],
                                                'environment': {'set': {'"{name}_ROOT"' : '"{prefix}"',
                                                                        '"{name}_VERSION"' : '"{version}"',
                                                                        '"{name}_BIN"' : '"{prefix.bin}"',
                                                                        '"{name}_INC"' : '"{prefix.include}"',
                                                                        '"{name}_LIB"' : '"{prefix.lib}"'}}},
                                       'projections' : {'all' : '"{}-{{name}}/{{version}}"'.format(project)},
                                       'verbose' : True}}}}

    filedir, file = split(abspath(__file__))
    projectdir = dirname(filedir) + '/project/{}'.format(project)
    filename = projectdir + '/' + project + '-' + single_stack_compiler + '-' + single_stack_mpi + '-' + single_stack_cuda + '-spack.yaml'
    generate_file(filename, contents)
    replace_single_quotes(filename)

def spack_all_stacks_yaml(project, projmod):
    """
    Generate TPL YAML file.

    Parameters
    ----------
    project : String
        Project for which to generate this file.

    """
    INSTALL_PATH = environ['SPACK_CM_TPL_INSTALL_PATH']
    BP_INSTALL_PATH = environ['SPACK_CM_BASE_PACKAGES_INSTALL_PATH']
    C_INSTALL_PATH = environ['SPACK_CM_COMPILER_INSTALL_PATH']
    U_INSTALL_PATH = environ['SPACK_CM_UTILITY_INSTALL_PATH']
    SPACK_CM_UTILITY_COMPILER = environ['SPACK_CM_UTILITY_COMPILER']
    SPACK_CM_COMPILERS = env_var_list('SPACK_CM_COMPILERS')
    SPACK_CM_EXTERNAL_COMPILERS = env_var_list('SPACK_CM_EXTERNAL_COMPILERS')
    COMPILERS = [c for c in SPACK_CM_COMPILERS + SPACK_CM_EXTERNAL_COMPILERS if c]
    SPACK_CM_MPIS = env_var_list('SPACK_CM_MPIS')
    SPACK_CM_EXTERNAL_MPIS = env_var_list('SPACK_CM_EXTERNAL_MPIS')
    MPIS = [c for c in SPACK_CM_MPIS + SPACK_CM_EXTERNAL_MPIS if c]
    SPACK_CM_CUDAS = env_var_list('SPACK_CM_CUDAS')
    SPACK_CM_EXTERNAL_CUDAS = env_var_list('SPACK_CM_EXTERNAL_CUDAS')
    CUDAS = [c for c in SPACK_CM_CUDAS + SPACK_CM_EXTERNAL_CUDAS if c]
    
    for compiler in COMPILERS:
        for mpi in MPIS:
            for cuda in CUDAS:
                spack_single_stack_yaml(project, projmod, compiler, mpi, cuda)


def generate_yamls(project, machine, path, projmod, machine_path,
                   generate_single_stacks, explicit_install_path,
                   explicit_modulefiles_path):
    """
    Generate all YAML files.

    Parameters
    ----------
    project : String
        Project for which to generate files.
    machine : String
        The machine for which to install packages.
    path : String
        The root path for installation and module file generation.
    projmod : Boolean
        Turn on project name in module generation. The default is True.
    machine_path: Boolean
        Add the machine name to the install path.

    """
    if(generate_single_stacks):
        try:
            export_env_vars(project, machine, path, machine_path, explicit_install_path, explicit_modulefiles_path)
            spack_all_stacks_yaml(project, projmod)
        except Exception as e:
            error = 'ERROR: Unable to generate YAML files with error:\n {}'.format(e)
            logger.critical(error)
            raise GenerateException(f"{pcolors.FAIL}" + error + f"{pcolors.ENDC}")
    else:
        try:
            export_env_vars(project, machine, path, machine_path, explicit_install_path, explicit_modulefiles_path)
            spack_base_package_yaml(project)
            spack_lmod_yaml(project)
            spack_compilers_yaml(project, projmod)
            spack_utilities_yaml(project, projmod)
            spack_tpl_yaml(project, projmod)
            spack_all_stacks_yaml(project, projmod)
        except Exception as e:
            error = 'ERROR: Unable to generate YAML files with error:\n {}'.format(e)
            logger.critical(error)
            raise GenerateException(f"{pcolors.FAIL}" + error + f"{pcolors.ENDC}")
