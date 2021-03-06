# -*- coding: utf-8 -*-

# DO NOT EDIT THIS FILE!
# This file has been autogenerated by dephell <3
# https://github.com/dephell/dephell

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import os.path

readme = ''
here = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(here, 'README.rst')
if os.path.exists(readme_path):
    with open(readme_path, 'rb') as stream:
        readme = stream.read().decode('utf8')

setup(
    long_description=readme,
    name='allennlp-multi-label',
    version='0.1.0',
    description='A multi-label classification plugin for AllenNLP.',
    python_requires='==3.*,>=3.6.1',
    project_urls={
        "repository": "https://github.com/semantic-health/allennlp-multi-label"
    },
    author='johngiorgi',
    author_email='johnmgiorgi@gmail.com',
    license='Apache-2.0',
    keywords='pytorch allennlp transformers document classification multi-label',
    classifiers=[
        'Development Status :: 1 - Planning', 'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Typing :: Typed'
    ],
    packages=['allennlp_multi_label'],
    package_dir={"": "."},
    package_data={},
    install_requires=['allennlp'],
    dependency_links=[
        'git+https://github.com/allenai/allennlp.git#egg=allennlp'
    ],
    extras_require={
        "dev": [
            "black==20.*,>=20.8.0.b1", "codecov==2.*,>=2.1.10",
            "coverage==5.*,>=5.3.0", "dephell[full]==0.*,>=0.8.3",
            "flake8==3.*,>=3.8.4", "hypothesis==5.*,>=5.38.0",
            "pytest==6.*,>=6.1.1", "pytest-cov==2.*,>=2.10.1"
        ]
    },
)
