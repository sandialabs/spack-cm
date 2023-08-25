"""
Parser and driver for spack-cm

"""


from src.core.check import check, check_spack
from src.core.setup import setup_spaces
from src.core.installer import installer
from src.core.utilities import dir_path, get_hostname, pcolors
import logging
import argparse
logger = logging.getLogger(__name__)


class MainException(Exception):
    """Catch all parser exceptions"""
    pass


def buildParser():
    """
    Builds the command parser.

    """
    parser = argparse.ArgumentParser(description="The main function for spack-cm. \
            'spack-cm COMMAND [OPTIONS]'.")
    subparsers = parser.add_subparsers(title='commands', dest='command')
    parser_setup = subparsers.add_parser('setup',
                                         description='Run set up routine for a new project/machine combination.')
    parser_installer = subparsers.add_parser('install',
                                           description='Run install routine for a project/machine combination.')
    parser_setup.add_argument('-p', '--project',
                        action='store',
                        dest='project',
                        help='REQUIRED: Project for which to install TPLs (e.g., sems, pyomo, etc.).')
    parser_setup.add_argument('-m', '--machine',
                        action='store',
                        dest='althostname',
                        default=None,
                        help='OPTIONAL: Designate an alternate platform name \
                            (i.e., not the hostname of the machine).')
    parser_setup.add_argument('--spack',
                        action='store',
                        dest='spackbranch',
                        default='v0.16.2',
                        help='OPTIONAL: Branch of spack. Default: v0.16.2')

    parser_installer.add_argument('-p', '--project',
                        action='store',
                        dest='project',
                        help='REQUIRED: Project for which to install TPLs (e.g., sems, pyomo, etc.).')
    parser_installer.add_argument('-m', '--machine',
                        action='store',
                        dest='althostname',
                        default=None,
                        help='OPTIONAL: Designate an alternate platform name \
                            (i.e., not the hostname of the machine).')
    parser_installer.add_argument('-r', '--root',
                        action='store',
                        type=dir_path,
                        dest='root_path',
                        help='REQUIRED: Root path in which to install TPLs (e.g. /project/sems, /project/pyomo, etc.).')
    parser_installer.add_argument('-s', '--stage',
                        action='store',
                        dest='stage',
                        default='all',
                        help='OPTIONAL: Select a single stage of the \
                            install to run. By default, all stages will \
                            run.\
                            Available choices: \
                            [base, compiler, utility, tpl]')
    parser_installer.add_argument('--spack',
                        action='store',
                        dest='spackbranch',
                        default='v0.16.2',
                        help='OPTIONAL: Branch of spack. Default: v0.16.2')
    parser_installer.add_argument('--install-spack-deps',
                        action='store_true',
                        dest='spackdeps',
                        help='OPTIONAL: Install spack system dependencies.')
    parser_installer.add_argument('-d', '--debug',
                        action='store_true',
                        dest='debug',
                        help='OPTIONAL: Enable "spack --debug" install mode.')
    parser_installer.add_argument('-e', '--external',
                        action='store_true',
                        dest='external',
                        help='OPTIONAL: Allow spack to find and use system packages.')
    parser_installer.add_argument('--no-project-modules',
                        action='store_false',
                        dest='projmod',
                        help='OPTIONAL: Turn off use of project name in modulefile generation.')
    parser_installer.add_argument('--add-machine-to-install-path',
                        action='store_true',
                        dest='machine_path',
                        help='OPTIONAL: Add the machine name to the install path.')
    parser_installer.add_argument('--generate_single_stacks',
                        action='store_true',
                        dest='generate_single_stacks',
                        help='OPTIONAL: Generate generic single compiler x mpi x cuda spack.yaml files. Skip the install step')
    parser_installer.add_argument('--explicit-install-path',
                        action='store',
                        dest='user_specified_install_path',
                        help='OPTIONAL: Exactly specify the install path for the package installations.')
    parser_installer.add_argument('--explicit-modulefile-path',
                        action='store',
                        dest='user_specified_modulefile_path',
                        help='OPTIONAL: Exactly specify the install path for module installations')
    parser_installer.add_argument('--dry-run',
                        action='store_const',
                        dest='fake',
                        default='',
                        const='--fake',
                        help='OPTIONAL: Only do a dry-run of an install for trial or debug purposes without installing anything.')

    return parser


def main(arguments):
    project = arguments.project
    if project is None:
        error = "ERROR: Project is required. Please provide a project using the -p flag."
        logger.critical(error)
        raise MainException(f"{pcolors.FAIL}" + error + f"{pcolors.ENDC}")
    spackbranch = arguments.spackbranch
    if arguments.althostname is not None:
        machine = arguments.althostname
    else:
        machine = get_hostname()
    # Check spack
    logger.info('Run specs: Project {}, Platform {},\n \
                Spack branch {}'.format(project, machine,
                spackbranch))
    # Run setup
    if arguments.command == 'setup':
        check_spack(spackbranch)
        setup_spaces(project, machine)
    # Run install
    elif arguments.command == 'install':
        root_path = arguments.root_path
        user_specified_install_path = arguments.user_specified_install_path
        user_specified_modulefile_path = arguments.user_specified_modulefile_path
        
        if root_path is None:
            if user_specified_install_path is None and user_specified_modulefile_path is None:
                error = 'ERROR: Root path is required. Please provide a root path using the -r flag or specify exact paths with --explicit-install-path and --explicit-modulefile-path'
                logger.critical(error)
                raise MainException(f"{pcolors.FAIL}" + error + f"{pcolors.ENDC}")
        stage = arguments.stage
        debug = arguments.debug
        external = arguments.external
        spackdeps = arguments.spackdeps
        # Secret Joe Option
        projmod = arguments.projmod
        # Secret SEMS Option
        machine_path = arguments.machine_path
        generate_single_stacks = arguments.generate_single_stacks
        fake = arguments.fake
        if fake:
            print(f'{pcolors.WARN}****** DRY RUN ******{pcolors.ENDC}')
        check(spackbranch, spackdeps)
        installer(project, machine, root_path, stage,
                  debug, external, fake, projmod, machine_path,
                  generate_single_stacks, user_specified_install_path,
                  user_specified_modulefile_path)
    else:
        error = 'ERROR: Must select either setup or install. \
                        Please select one or the other.'
        logger.critical(error)
        raise MainException(f"{pcolors.FAIL}" + error + f"{pcolors.ENDC}")


def driver():
    logging.basicConfig(filename='TPL-log.log',
                        filemode='w',
                        format='%(levelname)s:%(filename)s:%(funcName)s: %(message)s',
                        level=logging.DEBUG)
    # Parse the arguments
    parser = buildParser()
    arguments = parser.parse_args()
    logger.info('START: Beginning package installation process.')
    try:
        main(arguments)
    finally:
        logger.info('END: Package installation process has finished.')
