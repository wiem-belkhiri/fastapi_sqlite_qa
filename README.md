# FastAPI + SQLite for QA SQL Practice

This project is a light and fast starter for practicing SQL syntax and API testing without a complex setup.

## Stack

- FastAPI
- SQLite
- Pytest
- Python 3.12

## Goal

Practice:
- HTTP CRUD endpoints
- basic SQL queries
- joins and aggregates
- test automation with pytest

## Run locally

```bash
cd fastapi_sqlite_qa
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open:
- http://127.0.0.1:8000/docs

## Run tests

```bash
pytest -q
```

## SQL practice ideas

- SELECT * FROM users;
- SELECT * FROM posts WHERE user_id = 1;
- SELECT u.name, COUNT(p.id) as post_count FROM users u LEFT JOIN posts p ON u.id = p.user_id GROUP BY u.id, u.name;
- UPDATE users SET email = 'new@email.com' WHERE id = 1;
- DELETE FROM posts WHERE id = 1;

This is a good base for a QA backend portfolio project.
