from setuptools import find_packages, setup

# Start the setup
setup(
    name="od_lib",
    packages=find_packages(exclude=["tests"]),
)
