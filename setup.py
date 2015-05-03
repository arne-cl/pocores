# This is your "setup.py" file.
# See the following sites for general guide to Python packaging:
#   * `The Hitchhiker's Guide to Packaging <http://guide.python-distribute.org/>`_
#   * `Python Project Howto <http://infinitemonkeycorps.net/docs/pph/>`_

from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
#NEWS = open(os.path.join(here, 'NEWS.rst')).read()


version = '0.1.0'

install_requires = [
    # List your project dependencies here.
    # For more details, see:
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
    "discoursegraphs", "unidecode", "brewer2mpl"
]


setup(name='pocores',
    version=version,
    description="coreference resolution for German",
    #long_description=README + '\n\n' + NEWS,
    long_description=README,
    # Get classifiers from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[c.strip() for c in """
        Development Status :: 3 - Alpha
        License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)
        Operating System :: OS Independent
        Programming Language :: Python :: 2.7
        Topic :: Software Development :: Libraries :: Python Modules
        Natural Language :: German
        Topic :: Text Processing :: Linguistic
        """.split('\n') if c.strip()],
    keywords='linguistics nlp coreference anaphora german',
    author='Arne Neumann',
    author_email='pocores.programming@arne.cl',
    url='https://github.com/arne-cl/pocores',
    license='AGPLv3+',
    packages=find_packages("src"),
    package_dir = {'': "src"},
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points={
        'console_scripts':
            ['pocores=pocores.main:run_pocores_with_cli_arguments']
    }
)
