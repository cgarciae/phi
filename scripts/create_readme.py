
import phi
import os


with open('phi/version.txt', 'r') as f:
    version = f.read()

with open('phi/README-template.md', 'r') as f:
    readme = f.read().format(version)


with open('README.md', 'w') as f:
    f.write(readme)

