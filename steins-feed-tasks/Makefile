.PHONY: redis
redis:
	docker run -d -p 6379:6379 redis

.PHONY: worker
worker:
	python3 scripts/worker.py --loglevel=INFO

.PHONY: result
result:
	celery -A steins_feed_tasks result $(RESULT_ID)

.PHONY: add
add:
	celery -A steins_feed_tasks call steins_feed_tasks.dummy.add -a "[$(LEFT), $(RIGHT)]"

.PHONY: parse_feeds
parse_feeds:
	celery -A steins_feed_tasks call steins_feed_tasks.etl.parse_feeds

.PHONY: train_classifier
train_classifier:
	celery -A steins_feed_tasks call steins_feed_tasks.magic.train_classifier --args='[$(USER_ID), "$(LANGUAGE)"]'

.PHONY: train_classifiers
train_classifiers:
	python3 scripts/train_classifiers_all.py

.PHONY: analyze_text
analyze_text:
	celery -A steins_feed_tasks call "steins_feed_tasks.magic.analyze_text" --args='["$(S)", $(USER_ID), "$(LANGUAGE)"]'
