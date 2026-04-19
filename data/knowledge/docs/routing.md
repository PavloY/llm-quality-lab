# FastAPI Routing

## Basic Route Definition

FastAPI uses Python decorators to define routes. Each route maps an HTTP method and URL path to a Python function. The main HTTP method decorators are `@app.get()`, `@app.post()`, `@app.put()`, `@app.delete()`, and `@app.patch()`.

Example of a simple GET route:

    from fastapi import FastAPI

    app = FastAPI()

    @app.get("/")
    def read_root():
        return {"message": "Hello, World!"}

    @app.post("/items")
    def create_item(name: str):
        return {"name": name, "status": "created"}

## Path Parameters

Path parameters are declared in the route path using curly braces and must match function argument names. FastAPI automatically validates the type based on the Python type hint.

    @app.get("/items/{item_id}")
    def read_item(item_id: int):
        return {"item_id": item_id}

If you send a request to `/items/abc`, FastAPI will return a 422 Validation Error because `abc` is not a valid integer. You can use `str`, `int`, `float`, `bool`, and `uuid.UUID` as path parameter types.

For predefined path values, use Python Enum:

    from enum import Enum

    class ModelName(str, Enum):
        alexnet = "alexnet"
        resnet = "resnet"

    @app.get("/models/{model_name}")
    def get_model(model_name: ModelName):
        return {"model": model_name.value}

## Query Parameters

Any function parameter that is not part of the path is automatically treated as a query parameter. Query parameters are the key-value pairs that appear after `?` in the URL.

    @app.get("/items")
    def list_items(skip: int = 0, limit: int = 10):
        return {"skip": skip, "limit": limit}

A request to `/items?skip=5&limit=20` will set skip=5 and limit=20. Default values make query parameters optional. To make a query parameter required, do not provide a default value.

You can also use `Optional` for nullable query params:

    from typing import Optional

    @app.get("/search")
    def search(q: Optional[str] = None):
        if q:
            return {"results": f"Searching for: {q}"}
        return {"results": "No query provided"}
