import os
from setuptools import setup

# Dynamically calculate the version based on mydjango.VERSION
version = __import__('mydjango').__version__

def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages = []
root_dir = os.path.dirname(__file__)
module_dir = os.path.join(root_dir, 'mydjango')
pieces = fullsplit(root_dir)
if pieces[-1] == '':
    len_root_dir = len(pieces) - 1
else:
    len_root_dir = len(pieces)

for dirpath, dirnames, filenames in os.walk(module_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)[len_root_dir:]))


setup(
    name='my-django',
    version=version,
    license="MIT",
    description = 'Various Django helpers and extensions, chiefly Text Blocks.',
    author='Dmitri Fedortchenko',
    author_email='d@angelhill.net',
    url='https://github.com/zeraien/my-django/',
    packages=packages,
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
