# Development

Here's how to get started with Horseradish. The basic architecture is inspired
by [netflix lemur](https://github.com/netflix/lemur).

## Dependencies

### Python

Using `virtualenv`, but feel free to swap it out for your preferred python
environment manager.

```python
$ sudo pip install --upgrade pip
$ sudo pip install virtualenv
$ sudo pip install virtualenvwrapper
$ mkvirtualenv horseradish
$ (horseradish) pip install --upgrade pip
$ (horseradish) pip install "setuptools>=0.9.8"
$ (horseradish) pip install --upgrade pip-tools
$ (horseradish) pip-compile --output-file requirements.txt requirements.in -U --no-index
$ (horseradish) pip install -e .
$ (horseradish) pre-commit install
$ (horseradish) pre-commit run --all-files  # just to verify that the repo is in good shape
```

`workon horseradish` to activate the
`horseradish` Python environment. You can always disable the linting+style check steps with
`pre-commit uninstall`.

### Postgres

Install PostgreSQL: https://postgresapp.com/downloads.html.

Add PostgreSQL Tools to your `$PATH`:
`export PATH="$PATH:/Applications/Postgres.app/Contents/Versions/{version}/bin/"`
(substitute {version} of PostgreSQL.)

Initialize the database:

```
$ psql
postgres=# CREATE USER horseradish WITH PASSWORD '{pw}' SUPERUSER;  # superuser needed for pg_trgm extension
postgres=# CREATE DATABASE horseradish;
```

### Environment variables

None yet, but soon.

### Create initial config

`horseradish create_config`
`cd horseradish`
`horseradish -c ../horseradish.conf.py init`

## Running the server

`horseradish -c horseradish.conf.py runserver -p 8000`

## Coding standards

Horseradish follows [pep8](http://www.python.org/dev/peps/pep-0008/) with some
exceptions for line length and suppressing some warnings related to [black](https://github.com/psf/black), the code style of choice.

## Contributing

PRs are welcome, though they'll need to pass TravisCI checks before merging.
