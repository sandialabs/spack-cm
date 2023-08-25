# Spack Configuration Manager (Spack-CM)

[![Project Status: Unsupported – The project has reached a stable, usable state but the author(s) have ceased all work on it.](https://www.repostatus.org/badges/latest/unsupported.svg)](https://www.repostatus.org/#unsupported)

**NOTE**: Spack-CM was designed for earlier versions of spack (e.g., 0.16.0).
Newer functionality renders it relatively useless; however, it can still be
useful for those who are using older versions.

The Software Engineering Maintenance and Support (SEMS) operations and
maintenance (O&M) team is proud to present the Spack Configuration Manager
(spack-cm).

This tool leverages [Spack](https://github.com/spack/spack) to install 
compilers, utilities, and TPLs. It creates [Spack environments](https://spack-tutorial.readthedocs.io/en/latest/tutorial_environments.html) 
for each project with customizations available based on the platform (or machine).

## Requirements
Spack-cm has several core requirements:

1. [Spack](https://github.com/spack/spack)
2. [Python 3.7+](https://www.python.org/downloads/)
3. [PyYAML](https://pypi.org/project/PyYAML/)

We recommend, as a best practice, that a building area directory be created:
```
$ cd ~/
$ mkdir tpl_building
$ cd tpl_building
```

### 1. Spack

To install and activate spack, run the following:
```
# Get a copy of Spack
$ git clone https://github.com/spack/spack.git
# Activate Spack
$ source spack/share/spack/setup-env.sh
```

### 2. Python 3.7+

Most machines have a Python 3.7+ version already available. Run the
the following to confirm:
```
$ python3 --version
```

If the result returns anything Python 3.7+, this requirement is already
satisfied. If the result is an older Python or an error, you will
need to install Python either [from source](https://www.python.org/downloads/)
or using a package manager (such as `brew` on Macintosh).

#### WE RECOMMEND A VIRTUAL ENVIRONMENT
We recommend that all work be done in a virtual environment. This removes the 
need for administrator permissions and keeps your local Python environment
clean.

To create and activate a virtual environment, run:
```
# Create the environment
$ python3 -m venv ~/tpl_building/venv
# Activate the environment
$ source ~/tpl_building/venv/bin/activate
```

Please read the [`venv` documentation](https://docs.python.org/3/library/venv.html)
for more details.

### 3. PyYAML

`PyYAML` is available through the Python package installer `pip`. If you
are the administrator on the machine, you will be able to run:
```
$ pip install pyyaml
```

## Installation
To install, run:

```
$ cd ~/tpl_building
# Get a copy of the tool
$ git clone git@github.com:sandialabs/spack-cm.git
$ cd spack-cm
# Install the tool
$ python setup.py develop
```

This will install the command-line executable `spack-cm` that can be
run from anywhere. 

## Usage
There are two stages in the usage of this tool: `setup` and `install`.

### Setup
The `setup` phase of the `spack-cm` tool creates the required 
directory infrastructure for installation to run properly.

This step only needs to be run **ONCE** per project/machine combination, 
after which, the changes can be committed and pushed back to the `spack-cm`
repository for future use.

To complete this step, follow the below guidance:
```
$ spack-cm setup -h
usage: spack-cm setup [-h] [-p PROJECT] [-m ALTHOSTNAME] [--spack SPACKVERSION]

Run set up routine for a new project/machine combination.

optional arguments:
  -h, --help            show this help message and exit
  -p PROJECT, --project PROJECT
                        REQUIRED: Project for which to install TPLs (e.g., sems, pyomo, etc.).
  -m ALTHOSTNAME, --machine ALTHOSTNAME
                        OPTIONAL: Designate an alternate platform name (i.e., not the hostname of the machine).
  --spack SPACKVERSION  OPTIONAL: Version of spack. Default: 0.16.2
```
The `project` option is required, whereas the following two are optional. 

Upon running this command, it will create the file structure:
```
$ tree src/project/

src/project/
├── projectname
│   ├── projectname-manifest.yaml
│   ├── projectname-repo
│   │   ├── packages
│   │   └── repo.yaml
│   └── repos.yaml

$ tree src/platform/

src/platform/
├── machinename
│   ├── licenses
│   ├── compilers.yaml
│   ├── mirrors.yaml
│   └── packages.yaml
```
Under `src/project`, a directory named after your project will be created. 
In addition, there will be a file `projectname-manifest.yaml`, which is covered 
in the Required Customization section below.

Under `src/platform`, a directory named after your machine will be created. 
In addition, several empty `YAML` files that can be utilized by `spack` are 
created, which are covered in the Optional Customization section below.

### Install
The `install` phase of the `spack-cm` tool runs the installation 
of your project's requested packages.

This step will need to be run anytime something needs to be installed.

**IMPORTANT**: Before you run this step, we advise that you `module purge`
or at least `module unload` any unnecessary modules. There are known issues
with certain environment variables set by loaded modules. You will
not want to unload any compilers that you plan to use
to build TPLs.

To complete this step, follow the below guidance:
```
$ spack-cm install -h
usage: spack-cm install [-h] [-p PROJECT] [-m ALTHOSTNAME] [-r ROOT_PATH] [-s STAGE] [--spack SPACKVERSION] [--install-spack-deps] [-d] [-e]
                                [--no-project-modules] [--add-machine-to-install-path] [--dry-run]

Run install routine for a project/machine combination.

optional arguments:
  -h, --help            show this help message and exit
  -p PROJECT, --project PROJECT
                        REQUIRED: Project for which to install TPLs (e.g., sems, pyomo, etc.).
  -m ALTHOSTNAME, --machine ALTHOSTNAME
                        OPTIONAL: Designate an alternate platform name (i.e., not the hostname of the machine).
  -r ROOT_PATH, --root ROOT_PATH
                        REQUIRED: Root path in which to install TPLs (e.g. /project/sems, /project/pyomo, etc.).
  -s STAGE, --stage STAGE
                        OPTIONAL: Select a single stage of the install to run. By default, all stages will run. Available choices: [base, compiler,
                        utility, tpl]
  --spack SPACKVERSION  OPTIONAL: Version of spack. Default: 0.16.2
  --install-spack-deps  OPTIONAL: Install spack system dependencies.
  -d, --debug           OPTIONAL: Enable "spack --debug" install mode.
  -e, --external        OPTIONAL: Allow spack to find and use system packages.
  --no-project-modules  OPTIONAL: Turn off use of project name in modulefile generation.
  --add-machine-to-install-path
                        OPTIONAL: Add the machine name to the install path.
  --dry-run             OPTIONAL: Only do a dry-run of an install for trial or debug purposes without installing anything.
```
As with the previous step, `project` is required. The `root_path` option is also
required. This option specifies where the packages should be installed. Under
the `root_path`, the installation tree will look like:

```
root_path/
├── install
│   └── projectname
│       ├── base-packages
│       ├── compiler
│       ├── lmod
│       ├── tpl
│       └── utility
└── modulefiles
    └── projectname
```

This allows multiple projects to install in the same `root_path` without
overwriting files.

## Required Customization
The installation is based on the list found in your project's manifest file. 
As mentioned in the Setup section, when a project area is created, a sample 
`projectname-manifest.yaml` file is also created, the contents of which are:
```
# Compiler with which base packages will be installed.
# NOTE: System compilers are unreliable for newer versions of some
# compilers, such as gcc-4.8.5 and gcc-10.X. We recommend a newer compiler.
# If left empty, SPACK_CM_BASE_COMPILER will default to the system compiler.
SPACK_CM_BASE_COMPILER:
- ''
# USER WARNING: This list should not be modified unless by an advanced user.
# Basic, common dependencies which will be built only once.
SPACK_CM_BASE_PACKAGES:
- autoconf
- automake
- bzip2
- curl
- diffutils
- gmp
- xz
- zlib
- zstd
# Compilers to be installed.
SPACK_CM_COMPILERS:
- gcc@7.3.0
- gcc@10.1.0
# Compilers NOT to be installed, but against which TPLs should be built.
# (e.g., externally installed compilers)
SPACK_CM_EXTERNAL_COMPILERS:
- ''
# Compiler with which utilities will be built.
# NOTE: System compilers are notoriously unreliable for newer versions of some
# utilities, such as CMake. We recommend a newer compiler.
# If left empty, SPACK_CM_UTILITY_COMPILER will default to the system compiler.
SPACK_CM_UTILITY_COMPILER:
- gcc@7.3.0
# Utilities to be installed.
SPACK_CM_UTILITIES:
- cmake
- git
- ninja
- vvtest
# MPIs to be installed.
SPACK_CM_MPIS:
- openmpi@4.0.5
# MPIs NOT to be installed, but against which TPLs should be built.
# (e.g., externally installed MPIs)
SPACK_CM_EXTERNAL_MPIS:
- ''
# Cudas to be installed.
SPACK_CM_CUDAS:
- ''
# Cudas NOT to be installed, but against which TPLs should be built.
# (e.g., externally installed cudas)
SPACK_CM_EXTERNAL_CUDAS:
- ''
# TPLs to be installed.
SPACK_CM_TPLS:
- hdf5@1.10.6
- parallel-netcdf@1.9.0
- parmetis@4.0.3
- superlu-dist@5.4.0
- superlu@4.3
# Exclude these combinations of TPLs/compilers
SPACK_CM_EXCLUDE_COMBOS:
- ''
```
This file must be customized to match the needs of your project and/or your platform
(some of the defaults aren't appropriate for Mac, for example). All items are 
expected to be present but can be empty strings (see `SPACK_CM_CUDAS` as an example).

Edit this file with your project's desired packages before running the
`install` phase.

## Optional Customization
Within the `machinename` directory, a `licenses` directory is created.
You may place an Intel `license.lic` file in this directory, which will
be used when installing Intel.

There are many `YAML` files that allow advanced customization of Spack which
are supplied in the `machinename` and `projectname` areas.

See the [Spack configuration docs](https://spack.readthedocs.io/en/latest/configuration.html) 
for more details.
