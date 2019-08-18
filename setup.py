# coding=utf-8
from setuptools import setup, find_packages

setup(
    name='py-irclib',
    version='0.3.0',
    python_requires=">=3.5",
    description="A simple library for working with the IRC protocol",
    url='https://github.com/TotallyNotRobots/py-irclib',
    author='linuxdaemon',
    author_email='linuxdaemon.irc@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='irc irc-parser',
    packages=find_packages(exclude=['tests']),
    install_requires=[],
)
