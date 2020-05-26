# -*- coding: utf-8 -*-
"""Setup configuration."""

from setuptools import find_packages
from setuptools import setup


setup(
    name="curibio.sdk",
    version="0.1",
    description="CREATE A DESCRIPTION",
    url="https://github.com/CuriBio/curibio.sdk",
    author="Curi Bio",
    author_email="eli@nanosurfacebio.com",
    license="MIT",
    package_dir={"": "src"},
    packages=find_packages("src"),
    namespace_packages=["curibio"],
    install_requires=["h5py>=2.10.0"],
    zip_safe=False,
    include_package_data=True,
)
