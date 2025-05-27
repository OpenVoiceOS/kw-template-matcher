import os.path
from os.path import join

import os
from setuptools import setup, find_packages

BASEDIR = os.path.abspath(os.path.dirname(__file__))


def get_version():
    """ Find the version"""
    version_file = os.path.join(BASEDIR, 'kw_template_matcher', 'version.py')
    major, minor, build, alpha = (None, None, None, None)
    with open(version_file) as f:
        for line in f:
            if 'VERSION_MAJOR' in line:
                major = line.split('=')[1].strip()
            elif 'VERSION_MINOR' in line:
                minor = line.split('=')[1].strip()
            elif 'VERSION_BUILD' in line:
                build = line.split('=')[1].strip()
            elif 'VERSION_ALPHA' in line:
                alpha = line.split('=')[1].strip()

            if ((major and minor and build and alpha) or
                    '# END_VERSION_BLOCK' in line):
                break
    version = f"{major}.{minor}.{build}"
    if int(alpha):
        version += f"a{alpha}"
    return version


def required(requirements_file):
    """ Read requirements file and remove comments and empty lines. """
    with open(os.path.join(BASEDIR, requirements_file), 'r') as f:
        requirements = f.read().splitlines()
        return [pkg for pkg in requirements
                if pkg.strip() and not pkg.startswith("#")]

PLUGIN_ENTRY_POINT = 'ovos-keyword-template-matcher=kw_template_matcher.opm:KeywordTemplateMatcher'


setup(
    name="keyword-template-matcher",
    version=get_version(),
    author="JarbasAI",
    author_email="jarbasai@mailfence.com",
    description="A lightweight Python utility for template expansion and matching with slots and fuzzy matching.",
    long_description=open(join(BASEDIR, 'README.md')).read(),
    long_description_content_type="text/markdown",
    url="https://github.com/TigreGotico/kw-template-matcher",  # Update with your repo URL
    packages=find_packages(),
    install_requires=required("requirements.txt"),
    entry_points={'opm.transformer.intent': PLUGIN_ENTRY_POINT},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',  # Adjust the required Python version as needed
)
