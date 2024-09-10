Generic single-database configuration.

`alembic revision --autogenerate -m "<message>"` to create new revision
`alembic upgrade head` to upgrade the database

### TODO

- parametrized database paths (provide the database to get configured when running the 'upgrade' command, i.e. for tests)