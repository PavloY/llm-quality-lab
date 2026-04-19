# 422 Validation Error in FastAPI

## What is 422 Unprocessable Entity

The 422 status code means FastAPI received your request but could not process it because the data failed validation. This is the most common error newcomers encounter. FastAPI uses Pydantic to validate all incoming data — path parameters, query parameters, request bodies, and headers.

When validation fails, FastAPI returns a detailed JSON response:

    {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "name"],
                "msg": "Field required",
                "input": {}
            }
        ]
    }

The `loc` field tells you exactly where the error is: `["body", "name"]` means the `name` field in the request body is missing.

## Common Causes

1. **Missing required fields**: Your Pydantic model expects `name: str` but the client did not send it.
2. **Wrong data type**: The model expects `price: float` but you sent `"abc"`.
3. **Path parameter type mismatch**: Route expects `/items/{item_id}` with `item_id: int`, but you sent `/items/hello`.
4. **Missing Content-Type header**: Sending JSON body without `Content-Type: application/json`.
5. **Sending form data instead of JSON**: Using `requests.post(url, data=...)` instead of `requests.post(url, json=...)`.

## How to Debug

Step 1: Read the error response carefully. The `loc` field is your best friend — it pinpoints the exact field and location.

Step 2: Check your request. Use `curl -v` or browser DevTools Network tab to see what is actually being sent.

Step 3: Compare your request with the auto-generated docs at `/docs` (Swagger UI). FastAPI shows the expected schema for every endpoint.

Step 4: Add a `RequestValidationError` handler to log the full error for debugging:

    from fastapi.exceptions import RequestValidationError

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request, exc):
        print(f"Validation error: {exc.errors()}")
        print(f"Request body: {exc.body}")
        raise exc
