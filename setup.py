from setuptools import setup
import os

VERSION = "0.3"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="datasette-import-table",
    description="Datasette plugin for importing tables from other Datasette instances",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Simon Willison",
    url="https://github.com/simonw/datasette-import-table",
    project_urls={
        "Issues": "https://github.com/simonw/datasette-import-table/issues",
        "CI": "https://github.com/simonw/datasette-import-table/actions",
        "Changelog": "https://github.com/simonw/datasette-import-table/releases",
    },
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=["datasette_import_table"],
    entry_points={"datasette": ["import_table = datasette_import_table"]},
    install_requires=["datasette", "httpx", "sqlite-utils"],
    extras_require={"test": ["pytest", "pytest-asyncio", "httpx", "pytest-httpx"]},
    tests_require=["datasette-import-table[test]"],
    package_data={"datasette_import_table": ["templates/*.html"]},
)
