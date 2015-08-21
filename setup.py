__author__ = 'chenkovsky'
from setuptools import setup, find_packages
import os
setup(
    name='pygoogle',
    version="1.0",
    description="Python library to Google services (google search, google translate, google ngram)",
    long_description="some useful google services for language processing.",
    classifiers=[],
    keywords='google search',
    author='chenkovsky',
    author_email='chenkov@yeah.net',
    url='http://github.com/chenkovsky/pygoogle',
    license='MIT',
    packages=find_packages(),
    entry_points={
        # -*- Entry points: -*-
    },
    package_data={'': ['user-agents.txt']},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
        "requests", "beautifulsoup4"
    ],
)
