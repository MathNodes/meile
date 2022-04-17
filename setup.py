# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md', encoding="utf-8") as f:
    readme = f.read()

setup(
    name='meile',
    version='0.4.3',
    description='Meile dVPN powered by the Sentinel Network',
    long_description=readme,
    long_description_content_type="text/markdown",
    author='MathNodes',
    author_email='freQniK@mathnodes.com',
    url='https://github.com/MathNodes/meile',
    license='MIT',
    keywords='vpn, dvpn, sentinel, crypto, tui, privacy, security ',
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=['requests',  'npyscreen', 'prettytable'],
    package_data={'meile': ['config.ini','logo.uni']},
    entry_points = {
        'console_scripts': ['meile = meile.meile:main'],
    }
)

