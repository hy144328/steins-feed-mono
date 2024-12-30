# Stein's feed -- ETL

`.env`:

```
DB_NAME=../steins.db
```

`crontab -e`:

```bash
0 * * * *   cd steins-feed-mono/steins-feed-etl && . .venv/bin/activate && python3 scripts/prod.py
```
