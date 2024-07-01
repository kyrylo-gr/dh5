"""Install dh5."""

import setuptools

NAME = "dh5"
AUTHOR = "kyrylo.gr | LKB-OMQ"
AUTHOR_EMAIL = "git@kyrylo.gr"
DESCRIPTION = "Data H5. Work with hdf5 as classical dictionary."


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def get_version() -> str:
    """Get version from __config__.py."""
    with open(f"{NAME}/__config__.py", "r", encoding="utf-8") as file:
        for line in file.readlines():
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    raise ValueError("Version not found")


setuptools.setup(
    name=NAME,
    version=get_version(),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=f"https://github.com/kyrylo-gr/{NAME}",
    packages=setuptools.find_packages(exclude=["tests", "tests.*", "docs", "docs.*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy",
        "h5py",
    ],
    extras_require={
        "all": [""],
        "dev": [
            "matplotlib",
            "pytest",
            "check-manifest",
        ],
    },
)
