# Stein's feed -- API

`.env`:

```
ACCESS_TOKEN_EXPIRE_SECONDS=86400
DB_NAME=../steins.db
SECRET_KEY=

BROKER_URL=redis://localhost:6379/0
RESULT_BACKEND=redis://localhost:6379/0
```

`SECRET_KEY`:

```bash
openssl rand -hex 32
```
