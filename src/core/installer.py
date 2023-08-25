"""
Install TPLs using Spack
"""

from os.path import split, abspath, dirname, isdir
from os import environ
import subprocess
from src.core.cleanup import cleanup, spack_license_cleanup
from src.core.packages import generate_packages_yaml
from src.core.generate import generate_yamls
from src.core.utilities import (copy_spack_yaml, check_project_yaml_files,
                                generate_compiler_yaml, pcolors)
import logging
logger = logging.getLogger(__name__)


class InstallException(Exception):
    """Catch all install exceptions"""
    pass


def do_install(project, debug, external, filename,
               total_attempts, fake, generate_modules=True,
               load=False):
    """
    Run the spack install in the appropriate spack environment.

    Parameters
    ----------
    project : String
        The project for which to install packages.
    debug : Boolean
        Turn on debug mode.
    external : Boolean
        Turn on 'spack external find'.
    filename : String
        Name of spack.yaml file to activate.
    total_attempts : Integer
        Number of spack install retries.
    fake : String
        Use the spack install --fake flag if the user is requesting a dry-run.
    generate_modules : Boolean, optional
        Generate modules for installed packages. The default is True.
    load : Boolean, optional
        Load and generate info about the compilers. The default is False.

    """
    filedir, file = split(abspath(__file__))
    projectdir = dirname(filedir) + '/project/{}'.format(project)
    attempt = 0
    copy_spack_yaml(project, filename)
    while attempt < total_attempts:
        cleanup(projectdir, external)
        try:
            with open(projectdir + '/spack.yaml', 'r') as f:
                print(50*'*')
                print(f.read())
                print(50*'*')
            if debug:
                cmd = 'spack env activate {} && spack install -v {} && spack env deactivate'.format(projectdir, fake)
            else:
                cmd = 'spack env activate {} && spack install {} && spack env deactivate'.format(projectdir, fake)
            install = subprocess.run(cmd, shell=True)
            if install.returncode != 0:
                attempt += 1
                copy_spack_yaml(project, filename)
                warn = 'WARNING. Packages did not successfully install. \n \
                       Attempt: {}/{}.'.format(attempt, total_attempts)
                logger.warning(f"{pcolors.WARN}" + warn + f"{pcolors.ENDC}")
                continue
            if load:
                generate_compiler_yaml(project)
            if generate_modules:
                modules = subprocess.run('spack env activate {} && spack module lmod refresh -y && spack env deactivate'.format(projectdir), shell=True)
                if modules.returncode != 0:
                    logger.critical('ERROR: Unable to generate modules for {}'.format(projectdir))
                    raise InstallException('ERROR: Unable to generate modules for {}'.format(projectdir))
                logger.info('Modulefiles successfully generated.')
                print(f'{pcolors.OKGREEN}Modulefiles successfully generated.{pcolors.ENDC}')
            logger.info(f'{pcolors.OKGREEN}COMPLETE. All packages successfully installed.{pcolors.ENDC}')
            print('Install complete!\n')
            break
        except Exception as e:
            attempt += 1
            copy_spack_yaml(project, filename)
            warn = 'WARNING. Packages did not successfully install with error \n {}. \n \
                       Attempt: {}/{}.'.format(e, attempt, total_attempts)
            logger.warning(f"{pcolors.WARN}" + warn + f"{pcolors.ENDC}")
    else:
        error = 'ERROR. Packages not successfully installed after {} attempts. \n\
                 Please check logs for details.'.format(total_attempts)
        logger.critical(error)
        raise InstallException(f"{pcolors.FAIL}" + error + f"{pcolors.ENDC}")


def install_base_packages(project, debug, external, fake):
    """
    Install packages as defined by SPACK_CM_BASE_PACKAGES

    Parameters
    ----------
    project : String
        The project for which to install packages.
    debug : Boolean
        Turn on debug mode.
    external : Boolean
        Turn on 'spack external find'.
    fake : String
        Use the spack install --fake flag if the user is requesting a dry-run.

    """
    if fake:
        print(f'{pcolors.WARN}****** DRY RUN ******{pcolors.ENDC}')
    logger.info('Installing base packages as defined by $SPACK_CM_BASE_PACKAGES.')
    print(f'{pcolors.OKCYAN}Installing base packages...{pcolors.ENDC}')
    do_install(project, debug, external,
               'base-packages-spack.yaml', 2, fake, generate_modules=False)
    generate_packages_yaml(environ['SPACK_CM_BASE_PACKAGES_INSTALL_PATH'])


def install_lmod(project, debug, external, fake):
    """
    Install Lmod.

    Parameters
    ----------
    project : String
        The project for which to install packages.
    debug : Boolean
        Turn on debug mode.
    external : Boolean
        Turn on 'spack external find'.
    fake : String
        Use the spack install --fake flag if the user is requesting a dry-run.

    """
    if fake:
        print(f'{pcolors.WARN}****** DRY RUN ******{pcolors.ENDC}')
    logger.info('Installing Lmod.')
    print(f'{pcolors.OKCYAN}Installing Lmod...{pcolors.ENDC}')
    do_install(project, debug, external,
               'lmod-spack.yaml', 2, fake, generate_modules=False)


def install_compilers(project, debug, external, fake):
    """
    Install compilers as defined by SPACK_CM_COMPILERS.

    Parameters
    ----------
    project : String
        The project for which to install packages.
    debug : Boolean
        Turn on debug mode.
    external : Boolean
        Turn on 'spack external find'.
    fake : String
        Use the spack install --fake flag if the user is requesting a dry-run.

    """
    """
    WORKFLOW:
        Install the compilers
        Load the first one (we can get a list easily from the environment var)
        Run spack compiler find
        Unload
        Load
        Run
        (etc. for as many compilers as we installed)
        Steal the contents of the spack.yaml from our environment
        Put in a new compilers.yaml that lives in SPACK_CM_COMPILERS_INSTALL_PATH
    """
    if fake:
        print(f'{pcolors.WARN}****** DRY RUN ******{pcolors.ENDC}')
    logger.info('Installing compilers as defined by $SPACK_CM_COMPILERS.')
    print(f'{pcolors.OKCYAN}Installing compilers...{pcolors.ENDC}')
    do_install(project, debug, external, 'compilers-spack.yaml', 2, fake,
               load=True)


def install_utilities(project, debug, external, fake):
    """
    Install utilities as defined by SPACK_CM_UTILITIES

    Parameters
    ----------
    project : String
        The project for which to install packages.
    debug : Boolean
        Turn on debug mode.
    external : Boolean
        Turn on 'spack external find'.
    fake : String
        Use the spack install --fake flag if the user is requesting a dry-run.

    """
    if fake:
        print(f'{pcolors.WARN}****** DRY RUN ******{pcolors.ENDC}')
    logger.info('Installing utilities as defined by $SPACK_CM_UTILITIES.')
    print(f'{pcolors.OKCYAN}Installing utilities...{pcolors.ENDC}')
    do_install(project, debug, external, 'utilities-spack.yaml', 2, fake)
    generate_packages_yaml(environ['SPACK_CM_UTILITY_INSTALL_PATH'])


def install_tpls(project, debug, external, fake):
    """
    Install TPLs as defined by SPACK_CM_TPLS, SPACK_CM_MPIS, and SPACK_CM_CUDAS.

    Parameters
    ----------
    project : String
        The project for which to install packages.
    debug : Boolean
        Turn on debug mode.
    external : Boolean
        Turn on 'spack external find'.
    fake : String
        Use the spack install --fake flag if the user is requesting a dry-run.

    """
    if fake:
        print(f'{pcolors.WARN}****** DRY RUN ******{pcolors.ENDC}')
    logger.info('Installing TPLs as defined by $SPACK_CM_MPIS, $SPACK_CM_CUDAS, and $SPACK_CM_TPLS.')
    print(f'{pcolors.OKCYAN}Installing TPLs...{pcolors.ENDC}')
    do_install(project, debug, external, 'tpl-spack.yaml', 3, fake)
    generate_packages_yaml(environ['SPACK_CM_TPL_INSTALL_PATH'],
                           compiler_info=True)


def installer(project, machine, path, stage, debug, external, fake, projmod,
              machine_path, generate_single_stacks,
              explicit_install_path, explicit_modulefiles_path):
    """
    Installer driver for all phases of TPL installation.

    Parameters
    ----------
    project : String
        The project for which to install packages.
    machine : String
        The machine for which to install packages.
    path : String
        The root path for installation and module file generation.
    stage : String
        The stage of installation to complete.
        Options: all, base, compiler, utility, tpl.
    debug : Boolean
        Turn on debug mode.
    external : Boolean
        Turn on 'spack external find'.
    fake : String
        Use the spack install --fake flag if the user is requesting a dry-run.
    projmod : Boolean
        Turn on replacement of $PROJECT_NAME in modules.yaml file.
    machine_path: Boolean
        Add the machine name to the install path.
    generate_single_stacks: Boolean
        Generate generic single compiler x mpi x cuda spack.yaml files.
        Skip the install step.
    explicit_install_path: String
        Exact installation root path to use. Default: None
    explicit_modulefiles_path: String
        Exact module files root path to use. Default: None

    """
    filedir, filename = split(abspath(__file__))
    projectdir = dirname(filedir) + '/project/{}'.format(project)
    if not isdir(projectdir):
        error = 'ERROR: Project directory {} does not exist.\n\
                        Please run "spack-cm setup" first.'.format(projectdir)
        logger.critical(error )
        raise InstallException(f"{pcolors.FAIL}" + error + f"{pcolors.ENDC}")
    machinedir = dirname(filedir) + '/platform/{}'.format(machine)
    if not isdir(machinedir):
        error = 'ERROR: Platform directory {} does not exist.\n\
                        Please run "spack-cm setup" first.'.format(machinedir)
        logger.critical(error)
        raise InstallException(f"{pcolors.FAIL}" + error + f"{pcolors.ENDC}")
    generate_yamls(project, machine, path, projmod, machine_path,
                   generate_single_stacks, explicit_install_path,
                   explicit_modulefiles_path)
    if generate_single_stacks:
        warn = "WARNING: Skipping install phase because generate_single_stacks is enabled."
        logger.warning(f"{pcolors.WARN}" + warn + f"{pcolors.ENDC}")
        exit(0)
    all_stages = False
    if stage == 'all':
        all_stages = True
    try:
        check_project_yaml_files()
        if stage == 'base' or all_stages:
            if environ['SPACK_CM_BASE_PACKAGES'] != '':
                install_base_packages(project, debug, external, fake)
            else:
                warn = "WARNING: base stage skipped because SPACK_CM_BASE_PACKAGES is empty."
                logger.warning(f"{pcolors.WARN}" + warn + f"{pcolors.ENDC}")
            install_lmod(project, debug, external, fake)
        if stage == 'compiler' or all_stages:
            if environ['SPACK_CM_COMPILERS'] != '':
                install_compilers(project, debug, external, fake)
            else:
                warn = "WARNING: compiler stage skipped because SPACK_CM_COMPILERS is empty."
                logger.warning(f"{pcolors.WARN}" + warn + f"{pcolors.ENDC}")
        if stage == 'utility' or all_stages:
            if environ['SPACK_CM_UTILITIES'] != '':
                install_utilities(project, debug, external, fake)
            else:
                warn = "WARNING: utility stage skipped because SPACK_CM_UTILITIES is empty."
                logger.warning(f"{pcolors.WARN}" + warn + f"{pcolors.ENDC}")
        if stage == 'tpl' or all_stages:
            if environ['SPACK_CM_TPLS'] != '':
                install_tpls(project, debug, external, fake)
            else:
                warn = "WARNING: tpl stage skipped because SPACK_CM_TPLS is empty."
                logger.warning(f"{pcolors.WARN}" + warn + f"{pcolors.ENDC}")
        logger.info('COMPLETE: All stages of installation have successfully completed.')
        print('\n' + 50*'*')
        print(f'{pcolors.OKBLUE}COMPLETE: All stages of installation have successfully completed.{pcolors.ENDC}')
    except Exception:
        error = 'ERROR: Installation failed. See logs for details.'
        logger.critical(error)
        print(f"{pcolors.FAIL}" + error + f"{pcolors.ENDC}")
    finally:
        spack_license_cleanup()
