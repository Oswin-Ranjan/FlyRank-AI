
# CRUD API with PostgreSQL

A RESTful Task API built with **FastAPI** and **PostgreSQL**, supporting full CRUD (Create, Read, Update, Delete) operations. This project was developed for the **FlyRank Backend Internship – Week 3, Assignment BE-04**.

---

## What this is

This API manages tasks with three fields:

- **id** – Unique task ID
- **title** – Task title
- **done** – Task completion status

Unlike Assignment 1, task data is now stored in a **PostgreSQL database**, ensuring persistence and production-level reliability.

---

## Why PostgreSQL?

PostgreSQL was chosen because it:

- Supports strict data types like BOOLEAN and SERIAL
- Is widely used in production systems
- Handles concurrent users efficiently
- Provides better data integrity than SQLite
- Works seamlessly with Docker-based environments

---

## Why Docker?

Docker was used because it:

- Runs API and database in separate containers
- Eliminates the need for local database installation
- Ensures consistent setup across different systems
- Allows running the full stack with a single command

---

## Database

The application connects to PostgreSQL using:

DATABASE_URL=postgresql://postgres:dev@db:5432/tasks

On startup, the application:

- Creates the `tasks` table automatically
- Inserts three sample tasks only when the table is empty
- Does not duplicate sample tasks on future restarts

> **Note:** Data is persisted using Docker volumes, so it remains even after containers are restarted.

---

## How to Run

### 1. Create environment file

```bash
cp .env.example .env
```

### 2. Start the application

```bash
docker compose up --build
```

### 3. Open the API

API:

```
http://localhost:3000
```

Swagger UI:

```
http://localhost:3000/docs
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
curl -X POST http://localhost:3000/tasks \
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

C:\Users\ranja\OneDrive\Desktop\Documents\GitHub\FlyRank-AI\Week_3_Assignment\Assignment BE-04\image.png

---

## Technologies Used

- Python 3
- FastAPI
- PostgreSQL
- Psycopg
- Docker
- Docker Compose
- Uvicorn

---

## Assignment Features

- PostgreSQL database integration
- Automatic table creation
- Automatic seeding of sample tasks
- Persistent data storage using Docker volumes
- Parameterized SQL queries
- Full CRUD operations
- Swagger API documentation