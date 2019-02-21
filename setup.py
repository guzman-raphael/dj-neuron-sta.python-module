name = "dj_neuron"

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dj_neuron-rguzman",
    version="0.1.3",
    author="Raphael Guzman",
    author_email="raphael.h.guzman@gmail.com",
    description="Vathes engineering task submission.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/guzman-raphael/dj-neuron-sta.python-module",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
