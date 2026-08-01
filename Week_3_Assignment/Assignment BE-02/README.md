# CRUD API with SQLite

A RESTful Task API built with **FastAPI** and **SQLite**, supporting full CRUD (Create, Read, Update, Delete) operations. This project was developed for the **FlyRank Backend Internship – Week 3, Assignment A2**.

---

## What this is

This API manages tasks with three fields:

- **id** – Unique task ID
- **title** – Task title
- **done** – Task completion status

Unlike Assignment 1, task data is now stored in a **SQLite database (`tasks.db`)**, so it persists even after the server is restarted.

---

## Why SQLite?

SQLite was chosen because it:

- Is lightweight and serverless
- Requires no separate installation or configuration
- Stores all data in a single file (`tasks.db`)
- Automatically creates the database when the application starts
- Keeps data persistent across server restarts

---

## Database

The application automatically creates:

```
tasks.db
```

on startup if it doesn't already exist.

It also:

- Creates the `tasks` table automatically
- Inserts three sample tasks only when the table is empty
- Does not duplicate the sample tasks on future restarts

> **Note:** `tasks.db` is included in `.gitignore` so every fresh clone creates its own database automatically.

---

## How to Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the server

```bash
uvicorn app:app --reload
```

### 3. Open the API

API:

```
http://localhost:8000
```

Swagger UI:

```
http://localhost:8000/docs
```

---

## API Endpoints

| Method | Endpoint | Description | Success | Errors |
|--------|----------|-------------|---------|--------|
| GET | `/` | API information | 200 | — |
| GET | `/health` | Health check | 200 | — |
| GET | `/tasks` | List all tasks | 200 | — |
| GET | `/tasks/{id}` | Get task by ID | 200 | 404 |
| POST | `/tasks` | Create a task | 201 | 400 |
| PUT | `/tasks/{id}` | Update a task | 200 | 400, 404 |
| DELETE | `/tasks/{id}` | Delete a task | 204 | 404 |

---

## Example Request

```bash
curl -X POST http://localhost:8000/tasks \
-H "Content-Type: application/json" \
-d '{"title":"Buy milk"}'
```

Example Response

```json
{
    "id": 4,
    "title": "Buy milk",
    "done": false
}
```

---

## Example SQL Query

```sql
SELECT COUNT(*) FROM tasks;
```

**Output:**

Returns the total number of tasks currently stored in the database.

---

## Database Screenshot

<img width="3838" height="2038" alt="Screenshot 2026-07-26 230330-Picsart-AiImageEnhancer" src="https://github.com/user-attachments/assets/9f6bad38-8399-4c0d-b99f-dd1125675ac3" />

---

## Technologies Used

- Python 3
- FastAPI
- SQLite
- sqlite3
- Uvicorn

---

## Assignment Features

- SQLite database integration
- Automatic database creation
- Automatic table creation
- Automatic seeding of sample tasks
- Persistent data storage
- Parameterized SQL queries
- Full CRUD operations
- Swagger API documentation
