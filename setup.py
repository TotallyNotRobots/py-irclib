# coding=utf-8
from setuptools import setup

setup(
    name='py-irclib',
    version='0.2.0',
    python_requires=">=3.4",
    description="A simple library for working with the IRC protocol",
    url='https://github.com/TotallyNotRobots/py-irclib',
    author='linuxdaemon',
    author_email='linuxdaemon@snoonet.org',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='irc irc-parser',
    packages=['irclib', 'irclib.util'],
    install_requires=[],
    setup_requires=['pytest-runner', 'pytest-cov', 'pytest-pep8'],
    tests_require=['pytest', 'pytest-cov', 'pytest-pep8'],
)
