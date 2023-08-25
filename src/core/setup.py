"""
Set up Spack environment
"""

from os import mkdir
from os.path import isdir, split, abspath, dirname, join
from shutil import copyfile
import logging
logger = logging.getLogger(__name__)


class SetupException(Exception):
    """Catch all setup exceptions"""
    pass


def setup_spaces(project, machine):
    """
    Setup Spack environment files for a project/platform combo.

    Parameters
    ----------
    project : String
        Project for which environment is to be generated.
    machine : String
        Platform for which environment is to be generated.

    """
    print('Setting up spaces...')
    filedir, filename = split(abspath(__file__))
    projectdir = join(dirname(filedir), 'project', project)
    machinedir = join(dirname(filedir), 'platform', machine)
    machineExists = isdir(machinedir)
    if not machineExists:
        mkdir(machinedir)
        mkdir(join(machinedir, 'licenses'))
        mirrorfile = join(filedir, 'dMirrors.yaml')
        packagefile = join(filedir, 'dPackages.yaml')
        compilerfile = join(filedir, 'dCompilers.yaml')
        licensefile = join(filedir, 'license.lic')
        copyfile(mirrorfile, join(machinedir, 'mirrors.yaml'))
        copyfile(packagefile, join(machinedir, 'packages.yaml'))
        copyfile(compilerfile, join(machinedir, 'compilers.yaml'))
        copyfile(licensefile, join(machinedir, 'licenses', 'license.lic'))
        logger.info('SUCCESS: Machine space {} has been created.\
                    '.format(machine))
    else:
        logger.info('Machine space {} already exists.'.format(machine))
    projExists = isdir(projectdir)
    if not projExists:
        mkdir(projectdir)
        import spack.repo
        spack.repo.create_or_construct(projectdir + '/{}-repo'.format(
            project), project)
        packagefile = join(filedir, 'dPackages.yaml')
        reposfile = join(filedir, 'dRepos.yaml')
        manifestfile = join(filedir, 'manifestdestiny.yaml')
        copyfile(reposfile, join(projectdir, 'repos.yaml'))
        copyfile(manifestfile, join(projectdir, '{}-manifest.yaml'.format(project)))
        copyfile(packagefile, join(projectdir, 'packages.yaml'))
        logger.info('SUCCESS: Project space {} has been created.\
                    '.format(project))
    else:
        logger.info('Project space {} already exists.'.format(project))
    print('Space setup complete.')
