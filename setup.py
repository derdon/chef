from distutils.core import setup

# FIXME: 3rd party package 'argparse' is required for 2.5
# FIXME: ponder about using brownie instead of a local recipe for using
# namedtuple in 2.5
# -> use distribute

setup(
    name='chef',
    description='an interpreter for the esoteric programming language Chef',
    long_description='',
    version='0.1a',
    author='Simon Liedtke',
    author_email='liedtke.simon@googlemail.com',
    url='http://pypi.python.org/pypi/chef',
    license='ISC',
    packages=[
        'chef',
        'chef.errors',
        'chef.external',
        'chef.tests',
    ],
    scripts=['bin/chef'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Interpreters',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7']
)
