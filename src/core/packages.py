"""
Create packages.yaml file
"""

from src.core.utilities import pcolors
from os import makedirs
from os.path import isdir, isfile
import json
import yaml
import logging
logger = logging.getLogger(__name__)


class PackagesException(Exception):
    """Catch all packages exceptions"""
    pass


def generate_packages_yaml(path, compiler_info=True):
    """
    Generate a packages.yaml based on the Spack-generated
    .spack-db/index.json file.

    Parameters
    ----------
    path : String
        Full path to an installation location.
    compiler_info: Boolean
        Add compiler info to the spec in packages.yaml. The default is True.

    """
    if not isdir(path):
        try:
            makedirs(path)
        except Exception as e:
            error = 'ERROR: Creation of {} failed with error {}.'.format(path, e)
            logger.critical(error)
            raise PackagesException(f"{pcolors.FAIL}" + error + f"{pcolors.ENDC}")
    packages_file = path + '/packages.yaml'
    if not isfile(packages_file):
        try:
            open(packages_file, 'w').close()
        except Exception as e:
            error = 'ERROR: Creation of {} failed with error {}.'.format(packages_file, e)
            logger.critical(error)
            raise PackagesException(f"{pcolors.FAIL}" + error + f"{pcolors.ENDC}")
    install_path = path
    path = install_path + '/.spack-db/index.json'
    logger.info('Creating new packages.yaml file in {}.'.format(packages_file))
    print('Creating new packages.yaml file in {}.'.format(packages_file))
    with open(path, 'r') as f:
        contents = json.load(f)
    installs = contents['database']['installs']
    packages = {'packages' : {}}
    try:
        for sha in installs.keys():
            package = list(installs[sha]['spec'].keys())[0]
            if package == 'py-setuptools':
                continue
            version = installs[sha]['spec'][package]['version']
            path = installs[sha]['path']
            if compiler_info:
                compiler = installs[sha]['spec'][package]['compiler']
                compiler = compiler['name'] + '@' + compiler['version']
                spec = package + '@' + version + '%' + compiler
                if 'dependencies' in installs[sha]['spec'][package]:
                    for key in installs[sha]['spec'][package]['dependencies'].keys():
                        if 'mpi' in key:
                            mpi = path.split('/')[-2:]
                            spec += '^' + mpi[0] + '@' + mpi[1]
            else:
                spec = package + '@' + version
            if package in packages['packages']:
                packages['packages'][package]['externals'].append({'spec' : spec,
                                                            'prefix' : path})
            else:
               packages['packages'][package] = {'buildable' : True,
                                                'externals' : []}
               packages['packages'][package]['externals'].append({'spec' : spec,
                                                            'prefix' : path})
        with open(packages_file, 'w') as f:
            yaml.dump(packages, f, sort_keys=False)
    except Exception as e:
        error = 'ERROR: Packages.yaml creation in {} failed with error {}.'.format(install_path, e)
        logger.critical(error)
        raise PackagesException(f"{pcolors.FAIL}" + error + f"{pcolors.ENDC}")
