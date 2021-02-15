"""
Setup file
"""
from pathlib import Path
from typing import Any, Dict

from setuptools import find_packages, setup

base_dir = Path(__file__).parent


def get_pkginfo() -> Dict[str, Any]:
    """Get pkginfo data"""
    # pylint: disable=exec-used
    p: Dict[str, Any] = {}
    with open(base_dir / "irclib" / "__pkginfo__.py") as f:
        exec(f.read(), p)

    return p


__pkginfo__ = get_pkginfo()

setup(
    name="py-irclib",
    version=__pkginfo__["version"],
    python_requires=">=3.6",
    description="A simple library for working with the IRC protocol",
    url="https://github.com/TotallyNotRobots/py-irclib",
    author=__pkginfo__["author"],
    author_email="linuxdaemon.irc@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="irc irc-parser",
    packages=find_packages(exclude=["tests"]),
    install_requires=["attrs"],
    test_requires=["pytest", "pytest-cov"],
)
