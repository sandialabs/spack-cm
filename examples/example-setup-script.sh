#!/bin/bash

PYTHON3_MODULE_NAME=python/3.7.3
SPACK_REPO_DIRECTORY=/home/projects/x86-64-rocm/spack
SPACK_CM_REPO_DIRECTORY=/home/projects/x86-64-rocm/spack-cm
SPACK_CM_PYTHON_VENV_DIRECTORY=/home/projects/x86-64-rocm/spack-cm/venv

################################################################

module load ${PYTHON3_MODULE_NAME}
which python3
python3 --version

if [[ -f ${SPACK_CM_PYTHON_VENV_DIRECTORY}/bin/activate ]]; then
  source ${SPACK_CM_PYTHON_VENV_DIRECTORY}/bin/activate
else
  python3 -m venv ${SPACK_CM_PYTHON_VENV_DIRECTORY}
  source ${SPACK_CM_PYTHON_VENV_DIRECTORY}/bin/activate
fi

source ${SPACK_REPO_DIRECTORY}/share/spack/setup-env.sh


if [[ ! -d ${SPACK_CM_REPO_DIRECTORY} ]]; then
  git clone git@github.com:sandialabs/spack-cm.git ${SPACK_CM_REPO_DIRECTORY}
fi

if [[ ! -f ${SPACK_CM_PYTHON_VENV_DIRECTORY}/bin/spack-cm ]]; then
  cd ${SPACK_CM_REPO_DIRECTORY}
  python setup.py develop
fi

which spack
which spack-cm
