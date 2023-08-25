"""
Spack Configuration Manager
"""

from os.path import join, dirname
from setuptools import setup

def read(fname):
    """
    Reads the README functions are prints them into the long_description in
    the setup routine.

    Parameters
    ----------
    fname : README file name

    Returns
    -------
    Rendered README

    """
    return open(join(dirname(__file__), fname)).read()


classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers/Administrators",
    "Programming Language :: Python",
    "Topic :: Software Engineering Maintenance and Support",
    "Topic :: Third-Party Libraries",
    "Topic :: TPLs",
    "Topic :: Automation",
    "Topic :: Spack",
]

requires = [
    'pyyaml',
]


def run_setup():
    """
    This functions holds the setup command. Rather than running setup directly,
    it is wrapped in a 'try-except' that will print out errors if they occur.
    """
    setup(
        name='Spack Configuration Manager',
        version='0.1',
        url='git@github.com:sandialabs/spack-cm.git',
        description='Spack Configuration Manager',
        long_description=read('README.md'),
        long_description_content_type='text/markdown',
        classifiers=classifiers,
        packages=['src', 'src.core'],
        package_data={"": ["*.yaml"]},
        keywords=['sems', 'tpls', 'spack'],
        python_requires='>=3.7',
        entry_points="""
        [console_scripts]
        spack-cm = src.core.main:driver
        """,
    )


try:
    run_setup()
except SystemExit as e:
    print(e)
