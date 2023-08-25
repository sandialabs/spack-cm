'''
Miscellaneous utilities for use by spack-cm
'''

import logging
import subprocess
import yaml
import argparse
from os.path import split, abspath, dirname, isdir, isfile, join, expanduser
from os import environ, listdir, mkdir, makedirs, walk
from shutil import copyfile
logger = logging.getLogger(__name__)


class UtilityException(Exception):
    """Catch all Utility exceptions"""
    pass


class pcolors:
    """
    Color-coding for warning and error messages.
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARN = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def dir_path(path):
    """
    Determines whether path exists and is a directory.

    Parameters
    ----------
    path : String
        Path.

    Raises
    ------
    argparse
        Error if passed path is not valid.

    """
    from os.path import abspath, expanduser
    if isdir(abspath(expanduser(path))):
        return abspath(expanduser(path))
    else:
        raise argparse.ArgumentTypeError(f"{pcolors.FAIL}ERROR: Path is not valid. Please make sure path exists.{pcolors.ENDC}")


def get_hostname():
    """
    Get or assign hostname of machine.

    Returns
    -------
    OS : String
        Machine name.

    """
    from socket import gethostname
    OS = gethostname()
    logger.info('Running on machine {}.'.format(OS))
    return OS


def spack_dependencies():
    """
    Install/load important packages that are normally too old to run properly
    if supplied by the system.
    (patch, curl, bzip2)

    """
    packages = ['bzip2', 'curl', 'patch']
    try:
        for package in packages:
            logger.info('Attempting to load {}.'.format(package))
            print('Attempting to load {}...'.format(package))
            load = subprocess.run('spack find -p -d {}'.format(package),
                                  shell=True, stdout=subprocess.PIPE,
                                  universal_newlines=True)
            if load.returncode != 0:
                warn = 'WARNING: Unable to load spack module {}.\n Attempting installation.'.format(package)
                logger.warning(warn)
                print(f"{pcolors.WARN}" + warn + f"{pcolors.ENDC}")
                logger.info('Installing package ({}) in spack root.'.format(package))
                print('Installing and loading {}...'.format(package))
                install = subprocess.run('spack install -y {}'.format(package),
                                         shell=True)
                if install.returncode != 0:
                    error = 'ERROR: Package installation failed.\n \
                                    See spack logs for more details.'
                    logger.critical(error)
                    raise UtilityException(f"{pcolors.FAIL}" + error + f"{pcolors.ENDC}")
                load = subprocess.run('spack find -p -d {}'.format(package),
                                      shell=True, stdout=subprocess.PIPE,
                                      universal_newlines=True)
                if load.returncode != 0:
                    error = 'ERROR: Package load failed.\n \
                                    See spack logs for more details.'
                    logger.critical(error)
                    raise UtilityException(f"{pcolors.FAIL}" + error + f"{pcolors.ENDC}")
                else:
                    pathlist = [item for item in load.stdout.split() if item.startswith('/') and item != '/']
                    pathlist.reverse()
                    for path in pathlist:
                        environ['PATH'] = path + '/bin:' + environ['PATH']
                logger.info('Successfully installed and loaded {}.'.format(package))
                print('{} successfully installed and loaded.'.format(package))
            else:
                pathlist = [item for item in load.stdout.split() if item.startswith('/') and item != '/']
                pathlist.reverse()
                for path in pathlist:
                    environ['PATH'] = path + '/bin:' + environ['PATH']
                logger.info('Successfully loaded {}.'.format(package))
                print('{} successfully loaded.'.format(package))
    except Exception as e:
        error = 'ERROR: Necessary packages did not install/load successfully with error {}.'.format(e)
        logger.critical(error)
        raise UtilityException(f"{pcolors.FAIL}" + error + f"{pcolors.ENDC}")


def env_var_list(name):
    """
    Convert an environment variable from string to a list.

    Parameters
    ----------
    name : String
        Name of environment variable to convert to a list.

    """
    try:
        if len(environ[name]) > 1:
            env = environ[name].split(', ')
        else:
            env = [environ[name]]
        return env
    except Exception as e:
        error = 'ERROR: Environment variable conversion of string to list failed with error {}.'.format(e)
        logger.critical(error)
        raise UtilityException(f"{pcolors.FAIL}" + error + f"{pcolors.ENDC}")


def generate_file(file, contents):
    """
    Generate a YAML file.

    Parameters
    ----------
    file : String
        Path and name of output file.
    contents : String
        Contents to add to file.

    """
    class NoAliasDumper(yaml.SafeDumper):
        def ignore_aliases(self, data):
            return True
    with open(file, 'w') as f:
        yaml.dump(contents, f, sort_keys=False, Dumper=NoAliasDumper)


def check_project_yaml_files():
    """
    Check if the install path has the default yaml files and generate missing ones.

    """
    dir_yaml_path = [('compiler/', 'compilers.yaml'),
                     ('utility/', 'packages.yaml'),
                     ('base-packages/', 'packages.yaml')]
    for dir_path, yaml_file in dir_yaml_path:
        path = join(environ['SPACK_CM_INSTALL_PATH'], dir_path)
        if not isdir(path):
            try:
                makedirs(path)
            except Exception as e:
                error = 'ERROR: Creation of {} failed with error {}.'.format(path, e)
                logger.critical(error)
                raise UtilityException(f"{pcolors.FAIL}" + error + f"{pcolors.ENDC}")
        file = join(path, yaml_file)
        if not isfile(file):
            try:
                open(file, 'w').close()
            except Exception as e:
                error = 'ERROR: Creation of {} failed with error {}.'.format(yaml_file, e)
                logger.critical(error)
                raise UtilityException(f"{pcolors.FAIL}" + error + f"{pcolors.ENDC}")


def replace_single_quotes(filename):
    """
    Replace unnecessary single quotes in YAML files.

    Parameters
    ----------
    filename : String
        Path and name of file to be modified.

    """
    with open(filename, 'r') as f:
        data = f.read()
    new_data = data.replace("'", '')
    new_data = new_data.replace('?', "''")
    with open(filename, 'w') as f:
        f.write(new_data)


def export_env_vars(project, machine, root_path, machine_path,
                    explicit_install_path, explicit_modulefiles_path):
    """
    Export environment variables from project manifest file.

    Parameters
    ----------
    project : String
        Project for which environment is to be generated.
    machine : String
        Platform for which environment is to be generated.
    root_path : String
        Install/modulefile root path.
    machine_path: Boolean
        Add the machine name to the install path.
    explicit_install_path: String
        Use exactly this path for the package installations
    explicit_modulefiles_path: String
        Use exactly this path for modulefile installations
    """

    if explicit_install_path:
        install_path = explicit_install_path
    elif machine_path:
        install_path = join(root_path, 'install/{}/{}/'.format(machine, project))
    else:
        install_path = join(root_path, 'install/{}/'.format(project))

    if explicit_modulefiles_path:
        module_path = explicit_modulefiles_path
    elif machine_path:
        module_path = join(root_path, 'modulefiles/{}/{}/'.format(machine, project))
    else:
        module_path = join(root_path, 'modulefiles/{}/'.format(project))

    filedir, file = split(abspath(__file__))
    projectdir = join(dirname(filedir), 'project/{}'.format(project))
    machinedir = join(dirname(filedir), 'platform/{}'.format(machine))
    projectrepo = join(projectdir, '/repos.yaml')
    environ['SPACK_CM_PROJECT_REPO'] = projectrepo
    environ['SPACK_CM_PROJECT_NAME'] = project
    environ['SPACK_CM_MACHINE_NAME'] = machine
    environ['SPACK_CM_INSTALL_PATH'] = install_path
    environ['SPACK_CM_MODULEFILES_PATH'] = module_path
    environ['SPACK_CM_COMPILER_INSTALL_PATH'] = join(install_path, 'compiler')
    environ['SPACK_CM_UTILITY_INSTALL_PATH'] = join(install_path, 'utility')
    environ['SPACK_CM_TPL_INSTALL_PATH'] = join(install_path, 'tpl')
    environ['SPACK_CM_BASE_PACKAGES_INSTALL_PATH'] = join(install_path, 'base-packages')
    environ['SPACK_CM_LMOD_INSTALL_PATH'] = join(install_path, 'lmod')
    projectmanifest = join(projectdir, '{}-manifest.yaml'.format(project))
    subprocess.run('rm -rf ~/.spack && spack compiler find', shell=True)
    with open(join(expanduser('~/.spack'),
                   [subdir for subdir in listdir(expanduser('~/.spack')) if subdir != 'cache'][0]) + '/compilers.yaml', 'r') as f:
        comp = yaml.full_load(f)
        spec = comp['compilers'][0]['compiler']['spec']
        environ['SYSTEM_COMPILER'] = spec
    with open(projectmanifest, 'r') as f:
        contents = yaml.full_load(f)
    for key in contents:
        if key == 'SPACK_CM_UTILITY_COMPILER' and contents[key][0] == '':
            environ[key] = environ['SYSTEM_COMPILER']
            continue
        if key == 'SPACK_CM_BASE_COMPILER' and contents[key][0] == '':
            environ[key] = environ['SYSTEM_COMPILER']
            continue
        if contents[key] == '' or contents[key] == None:
            environ[key] = ''
            continue
        st = ', '
        environ[key] = st.join(contents[key])
    if 'intel' in environ['SPACK_CM_COMPILERS']:
        licensefile = join(machinedir, 'licenses/license.lic')
        spacklicense = join(environ['SPACK_ROOT'], 'etc/spack/licenses/intel')
        if not isdir(spacklicense):
            makedirs(spacklicense)
        copyfile(licensefile, join(spacklicense, 'license.lic'))
        logger.info('Copying license file {} to spack license area {}.'.format(licensefile, spacklicense))
        print('Copying license file {} to spack license area {}.'.format(licensefile, spacklicense))
    if environ['SPACK_CM_COMPILERS'] == '' and environ['SPACK_CM_EXTERNAL_COMPILERS'] == '':
        environ['SPACK_CM_EXTERNAL_COMPILERS'] = environ['SYSTEM_COMPILER']
    print('\n' + 50*'*')
    for key in environ:
        if 'SEMS' in key:
            logger.info('Environment path modified: {} is set to "{}".'.format(key, environ[key]))
            print('Environment path modified: {} is set to "{}".'.format(key, environ[key]))
    print('\n')


def copy_spack_yaml(project, filename):
    """
    Copy a generated YAML file into spack.yaml in the project directory.

    Parameters
    ----------
    project : String
        Project for which YAML is to be copied.
    file : String
        File name.

    """
    filedir, file = split(abspath(__file__))
    projectdir = join(dirname(filedir), 'project/{}'.format(project))
    copyfile(join(projectdir, filename), join(projectdir, 'spack.yaml'))


def generate_compiler_yaml(project):
    """
    Generate and copy a compilers.yaml into the compilers directory.

    Parameters
    ----------
    project : String
        Project for which YAML is to be generated.

    """
    filedir, file = split(abspath(__file__))
    projectdir = dirname(filedir) + '/project/{}'.format(project)
    compilers = env_var_list('SPACK_CM_COMPILERS')
    for compiler in compilers:
        logger.info('Attempting to load and gather info on compiler {}.'.format(compiler))
        load_compiler = subprocess.run('spack env activate {} && spack load {} && spack compiler find && spack unload {} && spack env deactivate'.format(projectdir, compiler, compiler), shell=True)
        if load_compiler.returncode != 0:
            logger.critical('ERROR: Was unable to load installed compiler {}.'.format(compiler))
            raise UtilityException('ERROR: Was unable to load installed compiler {}.'.format(compiler))
    compilers_file = join(environ['SPACK_CM_COMPILER_INSTALL_PATH'], 'compilers.yaml')
    with open(join(projectdir, 'spack.yaml'), 'r') as f:
        contents = yaml.full_load(f)
    contents = {'compilers': contents['spack']['compilers']}
    # Intel 19+ spack discovery nets the full version number (A.B.C.XYZ).
    # Rather than expect users to know the full number, which is not
    # available through Spack's interface, we will replace intel versions
    # with the A.B.C versioning scheme.
    i = 0
    for compiler in contents['compilers']:
        if 'intel' in compiler['compiler']['spec']:
            intel = compiler['compiler']['spec']
            contents['compilers'][i]['compiler']['spec'] = '.'.join(intel.split('.')[0:3])
        i += 1
    generate_file(compilers_file, contents)
    logger.info('Compilers successfully loaded.')
    print('Compilers successfully loaded.')


def generate_module_init_script(project, machine, lmod_install_path, module_file_install_path):
    """
    Generate a sourcable bash script for users to easily setup their module environment after they are generated

    Parameters
    ----------
    project : String
        Project for which init script is to be generated.
    machine : String
        Platform for which init script is to be generated.
    lmod_install_path : String
        Install/modulefile root path.
    module_file_install_path : String
        Install/modulefile root path.
    """    
    
    filedir, filename = split(abspath(__file__))
    projectdir = dirname(filedir) + '/project/{}'.format(project)

    for root, dirs, files in walk(lmod_install_path):
      if 'bash' in files:
          lmod_init_script_path = root

    script_install_path=projectdir + "/module-init-scripts/"
    if not isdir(script_install_path):
      mkdir(script_install_path)

    init_file_name = join(script_install_path, "{}-modules-{}-init.sh".format(project, machine))
    
    with open(init_file_name, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("\n")
        f.write("#If you want the only module you see to be those generated by this tool then uncomment below\n")
        f.write("#unset MODULEPATH\n")
        f.write("\n")
        f.write("#This will use the lmod installed by the tool instead of lmod or tcl on the system.\n")
        f.write("#lmod is required for the modules generated by this tool to work properly\n")
        f.write("source " + lmod_init_script_path + "/bash\n")
        f.write("\n")
        f.write("#source " + lmod_init_script_path + "/csh\n")
        f.write("\n")
        f.write("#Add the generated modules to your module path\n")
        f.write("module use " + module_file_install_path + "/Core\n")
