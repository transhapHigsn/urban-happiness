# Tracker Application

Tracker application tracks expenses among users.

## Getting started

### Environment setup

- Create virtual environment: `python3 -m virtualenv .venv --python=python3`
- Activate virtual environment: `source .venv/bin/activate`
- Install requirements: `pip install -r requirements.txt`

### Testing database setup

```sh
docker run -it -e POSTGRES_PASSWORD=passwd -e POSTGRES_USER=postgres -e POSTGRES_DB=tracker -p 5432:5432 postgres:alpine
```

### Migrating schema into database

```sh
source .venv/bin/activate
alembic upgrade head
```

### Running server

```sh
chmod +x ./runserver.sh # execute only once
./runserver.sh
```

Note: this will run server in debug mode.

## Features and associated endpoints

- Token for use in all apis: `/token` (token received should be passed in every following in header named "jwt")
- Track balance: `/track_balance`
- Organise Expenses: `/get_transactions`
- Add expenses: `/create_expense`
- Pay back: `/register_payback`

In order to use above, you will need to create user beforehand. You can do it by using `/create_user` endpoint.

Note: Attaching `postman collections` for understanding api calls.
