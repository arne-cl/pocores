import os
import sys
from setuptools import setup, find_packages
import platform

here = os.path.abspath(os.path.dirname(__file__))
#README = open(os.path.join(here, 'README.rst')).read()
#NEWS = open(os.path.join(here, 'NEWS.rst')).read()

version = '0.1.0'

install_requires = ["discoursegraphs"]


setup(name='pocores',
    version=version,
    description="graph-based coreference resolution for German",
    #~ long_description=README + '\n\n' + NEWS,
    # Get classifiers from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[c.strip() for c in """
        Development Status :: 2 - Pre-Alpha
        License :: OSI Approved :: GNU General Public License v3 (GPLv3)
        Operating System :: OS Independent
        Programming Language :: Python :: 2.7
        Topic :: Text Processing :: Linguistic
    """.split('\n') if c.strip()],
    keywords='linguistics nlp coreference anaphora german',
    author='Arne Neumann',
    author_email='pocores.programming@arne.cl',
    url='https://github.com/arne-cl/pocores',
    license='GPL Version 3',
    packages=['pocores'],
    package_dir = {'pocores': "src/pocores"},
    #~ package_data = {'pocores': ['data/*', 'grammar/*', 'avm.sty']},
    zip_safe=False,
    install_requires=install_requires,
    #~ entry_points={
        #~ 'console_scripts':
            #~ ['pocores=pocores.pocores:main']
    #~ }
)
