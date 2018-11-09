import setuptools
import os
import sys
from setuptools.command.install import install
import subprocess as sp
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info


class CustomInstallCommand(install):
    """Customized setuptools install command - prints a friendly greeting. for now"""

    def run(self):
        install.run(self)
        custom_command()


class CustomEggInfoCommand(egg_info):
    """Customized setuptools install command - prints a friendly greeting. for now"""

    def run(self):
        egg_info.run(self)
        custom_command()


class CustomDevelopCommand(develop):
    """Customized setuptools install command - prints a friendly greeting. for now"""

    def run(self):
        develop.run(self)
        custom_command()


def custom_command():
    if sys.platform == 'darwin':
         print("Installing tessaract")
         process = sp.Popen(['brew','install','tesseract'], stdout=sp.PIPE)
         for c in iter(lambda: process.stdout.read(1), b''): 
             sys.stdout.write(c)
        
    elif sys.platform == 'linux':
        os.system('sudo apt-get install tesseract-ocr')
    else:
        print("Do install tesseract for your system")


def parse_requirements(requirements):
    # load from requirements.txt
    with open(requirements) as f:
        lines = [l for l in f]
        # remove spaces
        stripped = map((lambda x: x.strip()), lines)
        # remove comments
        nocomments = filter((lambda x: not x.startswith('#')), stripped)
        # remove empty lines
        reqs = filter((lambda x: x), nocomments)
        return reqs


REQUIREMENTS = parse_requirements("requirements.txt")
setuptools.setup(
    name="DocScanner",
    version="1.0",
    url="https://github.com/unique1o1/DocScanner",
    author="Yunik Maharjan",
    author_email="yunik.maharjan@icloud.com",
    license='MIT',
    description="DocScanner",
    platforms="Linux, MacOS",
    long_description=open('README.md').read(),
    include_package_data=True,
    install_requires=["numpy==1.14.0",
                      "pdf2image==0.1.14",
                      "opencv_python==3.4.2.17",
                      "pytesseract==0.2.4",
                      "Pillow==5.2.0",
                      ],

    packages=setuptools.find_packages(),
    classifiers=[
        'Environment :: Console',
        'Programming Language :: Python :: 3.6'
    ],
    cmdclass={
        'install': CustomInstallCommand,
        'develop': CustomDevelopCommand,
        'egg_info': CustomEggInfoCommand
    },
    entry_points="""
    [console_scripts]
    docscan=DocScan.scan:run
    """,
)
