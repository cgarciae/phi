import os
from setuptools import setup
from pip.req import parse_requirements

# parse requirements
reqs = [str(r.req) for r in parse_requirements("requirements.txt", session=False)]


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()

version = read('phi/version.txt').split("\n")[0]

setup(
    name = "phi",
    version = version,
    author = "Cristian Garcia",
    author_email = "cgarcia.e88@gmail.com",
    description = ("Phi is a library for fluent functional programming in Python which includes a DSL + facilities to create libraries that integrate with it."),
    license = "MIT",
    keywords = ["functional programming", "DSL"],
    url = "https://github.com/cgarciae/phi",
   	packages = [
        'phi',
        'phi.tests'
    ],
    package_data={
        '': ['LICENCE', 'requirements.txt', 'README.md', 'CHANGELOG.md'],
        'phi': ['version.txt', 'README-template.md']
    },
    download_url = 'https://github.com/cgarciae/phi/tarball/{0}'.format(version),
    include_package_data = True,
    long_description = read('README.md'),
    install_requires = reqs
)
