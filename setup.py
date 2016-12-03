#!/usr/bin/env python
"""reqwire: a wrapper for easily managing requirements with pip-tools."""
from __future__ import absolute_import

import io
import sys

import setuptools


__all__ = ('setup',)


def readme():
    with io.open('README.rst') as fp:
        return fp.read()


def setup():
    """Package setup entrypoint."""
    extra_requirements = {
        ':python_version=="2.7"': ['enum34', 'pathlib2'],
    }
    install_requirements = [
        'atomicwrites',
        'biome',
        'emoji',
        'fasteners',
        'pip-tools',
        'requests',
    ]
    setup_requirements = ['six', 'setuptools>=17.1', 'setuptools_scm']
    needs_sphinx = {
        'build_sphinx',
        'docs',
        'upload_docs',
    }.intersection(sys.argv)
    if needs_sphinx:
        setup_requirements.append('sphinx')
    setuptools.setup(
        author='David Gidwani',
        author_email='david.gidwani@gmail.com',
        classifiers=[
            'Development Status :: 2 - Pre-Alpha',
            'Topic :: Software Development :: Libraries',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Utilities',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Operating System :: POSIX :: Linux',
            'Operating System :: Unix',
            'Operating System :: MacOS',
            'Operating System :: Microsoft :: Windows',
        ],
        description=__doc__,
        entry_points={
            'console_scripts': [
                'reqwire = reqwire.cli:main',
            ],
        },
        extras_require=extra_requirements,
        install_requires=install_requirements,
        license='MIT',
        long_description=readme(),
        name='reqwire',
        package_dir={'': 'src'},
        packages=setuptools.find_packages('./src'),
        setup_requires=setup_requirements,
        url='https://github.com/darvid/reqwire',
        use_scm_version=True,
        zip_safe=False,
    )


if __name__ == '__main__':
    setup()
