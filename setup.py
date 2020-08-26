#!/usr/bin/env python
import contextlib
import io
import os
import sys

from setuptools import setup

# Dependencies for this Python library.
REQUIRES = ["protobuf", "jinja2"]

HERE = os.path.dirname(os.path.abspath(__file__))


def setup_package():
    with chdir(HERE):
        packages = ["auto_proto_doc"]

        with io.open(
            os.path.join("auto_proto_doc", "_version.py"), "r", encoding="utf8"
        ) as f:
            about = {}
            exec(f.read(), about)

        try:
            with io.open("README.md", "r", encoding="utf8") as f:
                readme = f.read()
        except FileNotFoundError:
            readme = "# AUTODOC"
    setup(
        name=about["__title__"],
        version=about["__version__"],
        description=about["__summary__"],
        long_description=readme,
        author=about["__author__"],
        author_email=about["__author_email__"],
        url=about["__uri__"],
        packages=packages,
        install_requires=REQUIRES,
        entry_points={
            "console_scripts": ['protoc-gen-markdown=auto_proto_doc.generate:generate']
        },
        zip_safe=True,
        classifiers=[
            "Development Status :: 2 - Pre-Alpha",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
        ],
    )


@contextlib.contextmanager
def chdir(new_dir):
    old_dir = os.getcwd()
    try:
        os.chdir(new_dir)
        sys.path.insert(0, new_dir)
        yield
    finally:
        del sys.path[0]
        os.chdir(old_dir)


if __name__ == "__main__":
    setup_package()