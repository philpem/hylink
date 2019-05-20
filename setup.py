import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hylink",
    version="0.0.1.dev1",
    author="Phil Pemberton",
    author_email="philpem@philpem.me.uk",
    description="Hytera DMR radio interface library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/philpem/hylink",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Communications :: Ham Radio",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
)