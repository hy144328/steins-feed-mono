.PHONY: redis
redis:
	docker run -d -p 6379:6379 redis

.PHONY: worker
worker:
	celery -A steins_feed_tasks worker --loglevel=INFO

.PHONY: result
result:
	celery -A steins_feed_tasks result $(RESULT_ID)

.PHONY: add
add:
	celery -A steins_feed_tasks call steins_feed_tasks.dummy.add -a "[$(LEFT), $(RIGHT)]"

.PHONY: parse_feeds
parse_feeds:
	celery -A steins_feed_tasks call steins_feed_tasks.etl.parse_feeds

.PHONY: train_classifiers
train_classifiers:
	celery -A steins_feed_tasks call steins_feed_tasks.magic.train_classifiers_all

.PHONY: analyze_test
analyze_text:
	celery -A steins_feed_tasks call "steins_feed_tasks.magic.analyze_text" --args='["$(S)", $(USER_ID), "$(Language)"]'
