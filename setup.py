"""Install dh5."""
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dh5",
    version="0.7.8",
    author="LKB-OMQ",
    author_email="cryo.paris.su@gmail.com",
    description="Data H5. Work with hdf5 as classical dictionary.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kyrylo-gr/dh5",
    packages=setuptools.find_packages(exclude=["tests", "tests.*"]),
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
