# FastAPI Error Handling

## HTTPException

The simplest way to return an error response in FastAPI is to raise an `HTTPException`. This immediately stops request processing and returns an HTTP error response to the client.

    from fastapi import FastAPI, HTTPException

    app = FastAPI()

    items = {"foo": "The Foo Item"}

    @app.get("/items/{item_id}")
    def read_item(item_id: str):
        if item_id not in items:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"item": items[item_id]}

The `detail` parameter can be a string, dict, or list — FastAPI will serialize it to JSON automatically. The `status_code` should be a valid HTTP status code (4xx for client errors, 5xx for server errors).

You can also add custom headers to the error response:

    raise HTTPException(
        status_code=403,
        detail="Not enough permissions",
        headers={"X-Error": "Permission denied"},
    )

## Custom Exception Handlers

For more control over error responses, you can register custom exception handlers. This lets you catch specific exception types and return custom responses.

    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse

    class ItemNotFoundException(Exception):
        def __init__(self, item_id: str):
            self.item_id = item_id

    app = FastAPI()

    @app.exception_handler(ItemNotFoundException)
    async def item_not_found_handler(request: Request, exc: ItemNotFoundException):
        return JSONResponse(
            status_code=404,
            content={
                "error": "item_not_found",
                "message": f"Item {exc.item_id} does not exist",
                "path": str(request.url),
            },
        )

    @app.get("/items/{item_id}")
    def read_item(item_id: str):
        if item_id not in items:
            raise ItemNotFoundException(item_id)
        return {"item": items[item_id]}

## Overriding Default Exception Handlers

FastAPI has built-in handlers for validation errors and HTTP exceptions. You can override them:

    from fastapi.exceptions import RequestValidationError

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "error": "validation_error",
                "details": exc.errors(),
                "body": exc.body,
            },
        )

This is useful when you want a consistent error format across your entire API. Many teams define a standard error schema and override the default handlers to match it.

## Handling Unexpected Errors

For catching all unhandled exceptions (500 errors), add a generic handler:

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_server_error",
                "message": "An unexpected error occurred",
            },
        )

In production, make sure to log the actual exception for debugging while returning a generic message to the client.
