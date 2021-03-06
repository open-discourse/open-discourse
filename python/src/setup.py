from setuptools import find_packages, setup

setuptools_kwargs = {
    "install_requires": [
        "appdirs==1.4.4",
        "attrs==19.3.0",
        "beautifulsoup4==4.9.1",
        "black==19.10b0",
        "bs4==0.0.1",
        "certifi==2020.6.20",
        "chardet==3.0.4",
        "click==7.1.2",
        "DateTime==4.3",
        "dicttoxml==1.7.4",
        "flake8==3.8.3",
        "fuzzywuzzy==0.18.0",
        "idna==2.10",
        "importlib-metadata==1.7.0",
        "mccabe==0.6.1",
        "numpy==1.17.3",
        "pandas==0.25.3",
        "pathspec==0.8.0",
        "pycodestyle==2.6.0",
        "pyflakes==2.2.0",
        "python-dateutil==2.8.1",
        "pytz==2020.1",
        "regex==2020.7.14",
        "requests==2.24.0",
        "six==1.15.0",
        "soupsieve==2.0.1",
        "SQLAlchemy==1.3.18",
        "toml==0.10.1",
        "typed-ast==1.4.1",
        "urllib3==1.25.9",
        "zipp==3.1.0",
        "zope.interface==5.1.0",
    ]
}

# Start the setup
setup(
    name="od_lib",
    version="0.1",
    packages=find_packages(exclude=["tests"]),
    **setuptools_kwargs,
)
