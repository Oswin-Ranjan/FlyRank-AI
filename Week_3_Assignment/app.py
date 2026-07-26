from fastapi import FastAPI, HTTPException, Body
from database import init_db, get_connection

app = FastAPI()
init_db()

@app.get("/", summary="API info")
def root():
    """Returns basic info about this API and its endpoints."""
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health", summary="Health check")
def health():
    """Simple liveness check — returns ok if the server is running."""
    return {"status": "ok"}

@app.get("/tasks", summary="List all tasks")
def get_tasks():
    """Returns the full in-memory list of tasks."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": row["id"],
            "title": row["title"],
            "done": bool(row["done"])
        }
        for row in rows
    ]

@app.get("/tasks/{task_id}", summary="Get one task")
def get_task(task_id: int):
    """Returns a single task by id, or 404 if it doesn't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )

    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"])
    }

@app.post("/tasks", status_code=201, summary="Create a task")
async def create_task(body: dict = Body(...)):
    """Creates a new task from a JSON body with a 'title' field. 400 if title is missing or empty."""
    title = body.get("title", "")
    title = title.strip() if isinstance(title, str) else ""

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
    "INSERT INTO tasks(title, done) VALUES (?, ?)",
    (title, 0)
    )
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    
    return {
    "id": task_id,
    "title": title,
    "done": False
    }

@app.put("/tasks/{task_id}", summary="Update a task")
async def update_task(task_id: int, body: dict = Body(...)):
    """Updates title and/or done for an existing task. 404 if unknown id, 400 if body is invalid."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    )
    
    task = cursor.fetchone()
    
    if task is None:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )
        
    title = task["title"]
    done = bool(task["done"])

    if "title" in body:
        if not isinstance(body["title"], str) or not body["title"].strip():
            conn.close()
            raise HTTPException(
                status_code=400,
                detail="Title cannot be empty"
            )
        title = body["title"].strip()

    if "done" in body:
        if not isinstance(body["done"], bool):
            conn.close()
            raise HTTPException(
                status_code=400,
                detail="done must be true or false"
            )
        done = body["done"]

    cursor.execute(
        """
        UPDATE tasks
        SET title = ?, done = ?
        WHERE id = ?
        """,
        (title, int(done), task_id)
    )

    conn.commit()
    conn.close()

    return {
        "id": task_id,
        "title": title,
        "done": done
    }

@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    """Deletes a task by id. 404 if it doesn't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    )

    task = cursor.fetchone()

    if task is None:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )

    cursor.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )

    conn.commit()
    conn.close()