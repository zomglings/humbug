from setuptools import find_packages, setup

from infestor.version import INFESTOR_VERSION

long_description = ""
with open("README.md") as ifp:
    long_description = ifp.read()

setup(
    name="humbug-infestor",
    version=INFESTOR_VERSION,
    packages=find_packages(),
    install_requires=["atomicwrites", "bugout-locust", "humbug"],
    extras_require={
        "dev": ["black", "mypy", "wheel"],
        "distribute": ["setuptools", "twine", "wheel"],
    },
    description="Humbug Infestor: Manage Humbug reporting over your code base",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Bugout.dev",
    author_email="engineering@bugout.dev",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Software Development :: Libraries",
    ],
    url="https://github.com/bugout-dev/humbug",
)
