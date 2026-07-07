# League of Patches - Cassiopeia

A python based service built in FastAPI to interface with Anthropic or OpenAI LLMs to fetch and classify League of Legends patch notes for smart filtering and sorting.

## Getting started

Requires [uv](https://docs.astral.sh/uv/) and Python 3.12.

```bash
uv sync
cp .env.example .env

uv run uvicorn app.main:app --reload
uv run pytest
uv run ruff check .
```
