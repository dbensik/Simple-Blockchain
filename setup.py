# setup.py
from setuptools import setup, find_packages

# This is a shim for legacy support and editable installs.
# All project metadata is now in pyproject.toml.
setup(
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
