"""
Horseradish
=====
Is a tool for coding practice.
:copyright: (c) 2020 by Sam Havron, see AUTHORS for more
:license: Apache, see LICENSE for more details.
"""
from __future__ import absolute_import

# import datetime
# import json
# import logging
import os.path
import sys

# from subprocess import check_output

# from setuptools import Command
from setuptools import setup, find_packages

# from setuptools.command.develop import develop
from setuptools.command.install import install

# from setuptools.command.sdist import sdist

ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__)))

# When executing the setup.py, we need to be able to import ourselves, this
# means that we need to add the src/ directory to the sys.path.
sys.path.insert(0, ROOT)

about = {}
with open(os.path.join(ROOT, "horseradish", "__about__.py")) as f:
    exec(f.read(), about)  # nosec: about file is benign

# Parse requirements files
with open("requirements.txt") as f:
    install_requirements = f.read().splitlines()


class SmartInstall(install):
    """
    Installs Horseradish into the Python environment.
    If the package indicator is missing, this will also force a run of
    `build_static` which is required for JavaScript assets and other things.
    """

    def _needs_static(self):
        return not os.path.exists(os.path.join(ROOT, "horseradish/static/dist"))

    def run(self):
        # if self._needs_static():
        # self.run_command('build_static')
        install.run(self)


setup(
    name=about["__title__"],
    version=about["__version__"],
    author=about["__author__"],
    author_email=about["__email__"],
    url=about["__uri__"],
    description=about["__summary__"],
    long_description=open(os.path.join(ROOT, "README.md")).read(),
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requirements,
    # extras_require={
    #    'tests': tests_requirements,
    #    'docs': docs_requirements,
    #    'dev': dev_requirements,
    # },
    cmdclass={
        "install": SmartInstall
        # 'build_static': BuildStatic,
        # 'sdist': SdistWithBuildStatic,
    },
    entry_points={
        "console_scripts": [
            "horseradish = horseradish.manage:main",
        ],
        "horseradish.plugins": [],
    },
    classifiers=[
        "Framework :: Flask",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        "Programming Language :: Python :: 3.5",
        "Natural Language :: English",
        "License :: OSI Approved :: Apache Software License",
    ],
)
