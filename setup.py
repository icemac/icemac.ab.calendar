# -*- coding: utf-8 -*-
# Copyright (c) 2013 Michael Howitz
# See also LICENSE.txt

import os.path
import setuptools

def read(*path_elements):
    return file(os.path.join(*path_elements)).read()

version = '0.1.dev0'
long_description = '\n\n'.join([
    read('README.txt'),
    read('CHANGES.txt'),
    ])

setuptools.setup(
    name='icemac.ab.calendar',
    version=version,
    description="Calendar feature for icemac.addressbook",
    long_description=long_description,
    keywords='icemac.addressbook',
    author='Michael Howitz',
    author_email='icemac@gmx.net',
    url='http://pypi.python.org/pypi/icemac.ab.calendar',
    license='ZPL 2.1',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Paste',
        'Framework :: Zope3',
        'License :: OSI Approved',
        'License :: OSI Approved :: Zope Public License',
        'Natural Language :: English',
        'Natural Language :: German',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        ],
    packages=setuptools.find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages = ['icemac', 'icemac.ab'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # 'icemac.ab.locales > 0.11',
        'icemac.addressbook >= 1.9.1.dev0',
        'setuptools',
        ],
    extras_require = dict(
        test=[
            'icemac.addressbook [test]',
            'zope.testing >= 3.8.0',
            ]),
    entry_points = """
      [fanstatic.libraries]
      calendar_css = icemac.ab.calendar.browser.resource:css_lib
      """,
    )
