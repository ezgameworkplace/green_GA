# -*- coding: utf-8 -*-
"""
File:setup.py
Author:ezgameworkplace
Date:2023/7/10
"""
from setuptools import setup, find_packages


def parse_requirements(filename):
    with open(filename, 'r') as file:
        lines = (line.strip() for line in file)
        return [line for line in lines if line and not line.startswith('#')]


setup(
    name='green_GA',
    version='0.1.8',
    packages=find_packages(),
    author='ezgamer',
    author_email='hongzhang.ji@garena.com',
    description='A green lib for ga person.',
    install_requires=parse_requirements("requirements.txt"),
    include_package_data=True,
)
