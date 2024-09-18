# cars-rating-api

This was a recruitment assignment for a Junior Developer position.

# To run locally

Clone the repo and then:

(change CONTAINER_NAME to the name you want to assign)
```bash
$ docker run --name <CONTAINER_NAME> -p 5432:5432 -e POSTGRES_PASSWORD=mysecretpassword -d postgres  # obviously the password should not be included here, but as this is not an actual application I'm skipping setting up secrets
$ alembic upgrade head
$ fastapi dev src/main.py
```

# To make changes

- clone the repository
- run `pre-commit install` for automatic formatting / linting on commit

# To run tests

`pytest` from the main directory