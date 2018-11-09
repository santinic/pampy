import setuptools

from pampy import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pampy",
    version=__version__,
    author="Claudio Santini",
    author_email="hireclaudio@gmail.com",
    description="The Pattern Matching for Python you always dreamed of",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/santinic/pampy",
    packages=setuptools.find_packages(),
    platforms='any',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>3.6'
)
