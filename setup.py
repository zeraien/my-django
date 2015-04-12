import os
from setuptools import setup

# Dynamically calculate the version based on mydjango.VERSION
version = __import__('mydjango').__version__

setup(
    name='my-django',
    version=version,
    license="MIT",
    description = 'Various Django helpers and extensions, chiefly Text Blocks.',
    author='Dmitri Fedortchenko',
    author_email='d@angelhill.net',
    url='https://github.com/zeraien/my-django/',
    packages=['mydjango'],
    package_data={
        'mydjango.textblocks': ['templates/*.html', 'templates/*.js', 'static/*.gif'],
    },

    classifiers = ['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities'],
)
