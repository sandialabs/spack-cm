"""
Cleanup Spack files in between steps
"""

from src.core.utilities import pcolors
from os.path import isdir, expanduser, exists, join
from os import remove, environ
from shutil import rmtree
import logging
logger = logging.getLogger(__name__)


class CleanupException(Exception):
    """Catch all cleanup exceptions"""
    pass


def spack_cleanup(projectdir):
    """
    Cleans up system spack files.

    """
    if isdir(expanduser('~/.spack')):
        logger.info('Removing ~/.spack directory.')
        rmtree(expanduser('~/.spack'))
    if exists(join(projectdir, 'spack.lock')):
        print('Removing old spack.lock.')
        remove(join(projectdir, 'spack.lock'))
    if isdir(join(projectdir, '.spack-env')):
        print('Removing old spack environment.')
        rmtree(join(projectdir, '.spack-env'))
    from spack.main import SpackCommand
    clean = SpackCommand('clean')
    print(clean())


def spack_compiler_find():
    """
    Enable spack to find compilers.

    """
    from spack.main import SpackCommand
    compiler = SpackCommand('compiler')
    print(compiler('find'))
    logger.info("'spack compiler find' has been triggered.")


def spack_external_find():
    """
    Enable spack to find external packages.

    """
    from spack.main import SpackCommand
    print('Finding external packages.')
    external = SpackCommand('external')
    print(external('find'))
    logger.info("'spack external find' has been triggered.")

def spack_license_cleanup():
    """
    Remove any Intel licenses in SPACK_ROOT

    """
    spacklicense = join(environ['SPACK_ROOT'], 'etc/spack/licenses/intel')
    if isdir(spacklicense):
        rmtree(spacklicense)

def cleanup(projectdir, ext=False):
    """
    Complete Spack cleanup.

    Parameters
    ----------
    projectdir : String
        Project directory in which to clean up files.
    ext : Boolean, optional
        Turn on external package finder. The default is False.

    """
    try:
        spack_cleanup(projectdir)
        spack_compiler_find()
        if ext:
            spack_external_find()
        logger.info('Spack cleanup completed.')
    except Exception as e:
        error = 'ERROR: Spack cleanup was unsuccessful with error: \n{}'.format(e)
        logger.critical(error)
        raise CleanupException(f"{pcolors.FAIL}" + error + f"{pcolors.ENDC}")
