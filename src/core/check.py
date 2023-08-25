"""
Set up Spack
"""

from src.core.utilities import spack_dependencies, pcolors
from os import system, chdir
from os.path import dirname, join as osjoin
import logging
import subprocess
from sys import path as syspath
logger = logging.getLogger(__name__)


class CheckSpackException(Exception):
    """Catch all Spack setup exceptions"""
    pass


def check_spack(branch):
    """
    Set up spack for use with the application.

    Parameters
    ----------
    version : String
        Desired spack version.

    """
    print('Checking spack...')
    spack_root = subprocess.run(['which', 'spack'], stdout=subprocess.PIPE)
    if spack_root.returncode != 0:
        spack_exists = False
    else:
        spack_exists = True
        spack_root = dirname(dirname(spack_root.stdout.decode('utf-8').strip()))
    if not spack_exists:
        error = "ERROR: Spack not found on PATH. Please clone spack from https://github.com/spack/spack \n and run 'source $spack_root/share/spack/setup-env.(c)sh'."
        logger.critical(error)
        raise CheckSpackException(f"{pcolors.FAIL}" + error + f"{pcolors.ENDC}")

    else:
        # Check branch to make sure it's the correct branch
        spack_branch = subprocess.Popen(['git', 'status'], stdout=subprocess.PIPE).communicate()[0].decode('utf-8').split('\n')[0].split(' ')[-1]
        if spack_branch != branch:
            logger.info('INFO: Spack branch incorrect. Replaced {} with {}.'.format(spack_branch, branch))
            chdir(spack_root)
            system('git fetch && git checkout {} && git pull origin {}'.format(branch, branch))
            logger.info('Spack version was changed to {}.'.format(branch))
        else:
            logger.info('Local spack branch matches desired branch.')

    """
    Adding spack to Pythonpath so spack-python commands can be used.
    """
    spack_lib_path = osjoin(spack_root, "lib", "spack")
    syspath.insert(0, spack_lib_path)
    spack_external_libs = osjoin(spack_lib_path, "external")
    syspath.insert(0, spack_external_libs)


def check(version, spackdeps):
    check_spack(version)
    if spackdeps:
        spack_dependencies()
    print('Spack check complete.')
    logger.info('COMPLETE: Spack check has been completed.')
