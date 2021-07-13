#!/usr/bin/env python

from setuptools import setup, find_namespace_packages


INSTALL_REQUIRES = [
    'asyncstdlib',
    'pymongo==3.11.2',
    'fastapi==0.63.0',
    'jinja2==2.11.2',
    'aiohttp==3.7.3',
    'aiofiles==0.6.0',
    'python-multipart',
    'uvicorn==0.13.3',
]

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='booktracker',
    version='0.1',
    description='Tracks Apple books in collection',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
    ],
    url='https://github.com/pkpinto/booktracker',
    author='Paulo Kauscher Pinto',
    author_email='paulo.kauscher.pinto@icloud.com',
    license='Apache License 2.0',
    package_dir={'': 'src'},
    packages=find_namespace_packages(where='src'),
    include_package_data=True,
    package_data={'booktracker.web': ['static/*', 'static/*/*', 'templates/*']},
    install_requires=INSTALL_REQUIRES,
    entry_points={
        'console_scripts': [
            'bookt_api=booktracker.api.app:main',
            'bookt_web=booktracker.web.app:main',
        ],
    },
)
