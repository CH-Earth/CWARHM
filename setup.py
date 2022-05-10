from setuptools import setup
from setuptools import find_packages

with open("README.rst", "r") as f:
    long_description = f.read()

setup(
    name="CWARHM",
    version="0.1",
    description="Community Workflows to Advance Reproducibility in Hydrological Modelling",
    license="MIT",
    long_description=long_description,
    author="CH-EARTH - computational hydrology group at Centre for Hydrology, University of Saskatchewan",
    url="https://github.com/CH-Earth/CWARHM",
    packages=find_packages()
    # packages=['fairymwah']  #same as name
)
