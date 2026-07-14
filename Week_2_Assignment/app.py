from fastapi import FastAPI, HTTPException, Body

app = FastAPI()

tasks = [
    {"id": 1, "title": "Complete this assignment", "done": False},
    {"id": 2, "title": "Write README", "done": False},
    {"id": 3, "title": "Push to GitHub", "done": True},
]

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
    return tasks


@app.get("/tasks/{task_id}", summary="Get one task")
def get_task(task_id: int):
    """Returns a single task by id, or 404 if it doesn't exist."""
    task = next((t for t in tasks if t["id"] == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task

@app.post("/tasks", status_code=201, summary="Create a task")
async def create_task(body: dict = Body(...)):
    """Creates a new task from a JSON body with a 'title' field. 400 if title is missing or empty."""
    title = body.get("title", "")
    title = title.strip() if isinstance(title, str) else ""

    if not title:
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    task = {"id": max((t["id"] for t in tasks), default=0) + 1, "title": title, "done": False}
    tasks.append(task)
    return task

@app.put("/tasks/{task_id}", summary="Update a task")
async def update_task(task_id: int, body: dict = Body(...)):
    """Updates title and/or done for an existing task. 404 if unknown id, 400 if body is invalid."""
    task = next((t for t in tasks if t["id"] == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    if "title" in body:
        title = body["title"]
        if not isinstance(title, str) or not title.strip():
            raise HTTPException(status_code=400, detail="Title cannot be empty")
        task["title"] = title.strip()

    if "done" in body:
        if not isinstance(body["done"], bool):
            raise HTTPException(status_code=400, detail="done must be true or false")
        task["done"] = body["done"]

    return task

@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    """Deletes a task by id. 404 if it doesn't exist."""
    task = next((t for t in tasks if t["id"] == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    tasks.remove(task)