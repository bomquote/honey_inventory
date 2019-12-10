
from setuptools import setup, find_packages
from app.core.version import get_version

VERSION = get_version()

f = open('README.md', 'r')
LONG_DESCRIPTION = f.read()
f.close()

setup(
    name='app',
    version=VERSION,
    description='MyApp Does Amazing Things!',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Bob Jordan',
    author_email='bmjjr@bomquote.com',
    url='https://github.com/bmjjr/hg_inventory',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'tests*']),
    package_data={'app': ['templates/*']},
    include_package_data=True,
    entry_points="""
        [console_scripts]
        app = app.main:main
    """,
)
