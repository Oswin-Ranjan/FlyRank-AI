# Task API

A small in-memory to-do list API built with FastAPI, supporting full CRUD (Create, Read, Update, Delete) on tasks. Built for FlyRank Backend Internship — Week 2, Assignment A1.

## What this is

A REST API for managing tasks (id, title, done). Data is stored in memory only — it resets when the server restarts. Interactive docs are available via Swagger UI.

## How to run it

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the server:
   ```bash
   uvicorn main:app --reload
   ```

3. The API is now running at `http://localhost:8000`. Interactive docs (Swagger UI) are at `http://localhost:8000/docs`.

## Endpoints

| Method | Path          | Description                          | Success | Errors             |
|--------|---------------|---------------------------------------|---------|---------------------|
| GET    | `/`           | API info                              | 200     | —                    |
| GET    | `/health`     | Health check                          | 200     | —                    |
| GET    | `/tasks`      | List all tasks                        | 200     | —                    |
| GET    | `/tasks/{id}` | Get one task                          | 200     | 404 if not found     |
| POST   | `/tasks`      | Create a task (`{"title": "..."}`)    | 201     | 400 if title empty   |
| PUT    | `/tasks/{id}` | Update a task's title and/or done     | 200     | 404 / 400            |
| DELETE | `/tasks/{id}` | Delete a task                         | 204     | 404 if not found     |

## Example request

```
$ curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Buy milk"}'

HTTP/1.1 201 Created
content-type: application/json

{"id":4,"title":"Buy milk","done":false}
```

## Swagger UI

![Swagger UI screenshot](swagger-screenshot.png)

## Notes

- No database — data lives in a Python list in memory and resets on restart. Databases arrive in Week 3.
- Request bodies are read via FastAPI's `Body()` rather than a Pydantic model, by choice, to keep validation logic explicit and dependency-free.