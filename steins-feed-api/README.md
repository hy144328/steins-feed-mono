# Stein's feed -- API

`.env`:

```
ACCESS_TOKEN_EXPIRE_SECONDS=86400
SECRET_KEY=

# Model.
DB_USER=
DB_PASS=
DB_HOST=
DB_PORT=
DB_NAME=../steins.db

# Tasks.
BROKER_URL=redis://localhost:6379/0
RESULT_BACKEND=redis://localhost:6379/0
```

`SECRET_KEY`:

```bash
openssl rand -hex 32
```
