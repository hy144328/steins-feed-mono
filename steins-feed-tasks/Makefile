.PHONY: redis
redis:
	docker run -d -p 6379:6379 redis

.PHONY: worker
worker:
	celery -A steins_feed_tasks worker --loglevel=INFO
