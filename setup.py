
from setuptools import setup, find_packages
from honey.core.version import get_version

VERSION = get_version()

f = open('README.md', 'r')
LONG_DESCRIPTION = f.read()
f.close()

setup(
    name='honey-inventory',
    version=VERSION,
    description='Sweet command line inventory control',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Bob Jordan',
    author_email='bmjjr@bomquote.com',
    url='https://github.com/bomquote/honey-inventory',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'tests*']),
    package_data={'honey': ['templates/*']},
    include_package_data=True,
    entry_points="""
        [console_scripts]
        honey = honey.honey:main
    """,
)
