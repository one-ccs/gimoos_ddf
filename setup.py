#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


with open('README.md', 'r', encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name='gimoos_ddf',
    version='0.1.2',
    description='',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='',
    author_email='',
    url='',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.10',
    packages=find_packages(),
    package_dir={},
    package_data={},
    exclude_package_data={},
    install_requires=[],
    entry_points={
        'console_scripts': [
            'gimoos_ddf = gimoos_ddf.manager:main',
        ],
    },
)
