# steins-feed-mono

```mermaid
flowchart TD
    subgraph backend
    steins-feed-model --> steins-feed-config
    steins-feed-model --> steins-feed-etl
    steins-feed-model --> steins-feed-magic

    steins-feed-etl --> steins-feed-tasks
    steins-feed-magic --> steins-feed-tasks

    steins-feed-magic --> steins-feed-api
    steins-feed-model --> steins-feed-api
    steins-feed-tasks --> steins-feed-api
    end

    subgraph frontend
    steins-feed-ui
    end

    steins-feed-api -.-> steins-feed-ui
```
