# datasette-import-table

[![PyPI](https://img.shields.io/pypi/v/datasette-import-table.svg)](https://pypi.org/project/datasette-import-table/)
[![Changelog](https://img.shields.io/github/v/release/simonw/datasette-import-table?include_prereleases&label=changelog)](https://github.com/simonw/datasette-import-table/releases)
[![Tests](https://github.com/simonw/datasette-import-table/workflows/Test/badge.svg)](https://github.com/simonw/datasette-import-table/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/datasette-import-table/blob/main/LICENSE)

Datasette plugin for importing tables from other Datasette instances

**Warning: alpha software**. This doesn't yet have any permissions checking code.

## Installation

Install this plugin in the same environment as Datasette.

    $ datasette install datasette-import-table

## Usage

Visit `/-/import-table` for the interface. Paste in the URL to a table page on another Datasette instance and click the button to import that table.

## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:

    cd datasette-import-table
    python3 -mvenv venv
    source venv/bin/activate

Or if you are using `pipenv`:

    pipenv shell

Now install the dependencies and tests:

    pip install -e '.[test]'

To run the tests:

    pytest
