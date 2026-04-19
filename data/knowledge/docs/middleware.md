# FastAPI Middleware

## What is Middleware

Middleware in FastAPI is a function that processes every request before it reaches a route handler and every response before it is returned to the client. Middleware sits between the client and your application logic.

A basic custom middleware:

    from fastapi import FastAPI, Request
    import time

    app = FastAPI()

    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

The `call_next` function passes the request to the next middleware or route handler and returns the response.

## CORS Middleware

Cross-Origin Resource Sharing (CORS) is required when your frontend and backend are on different domains or ports. Without CORS configuration, browsers will block requests from your frontend to your API.

    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "https://myapp.com"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

Key CORS parameters:
- `allow_origins` — list of allowed origins (use `["*"]` for development only, never in production)
- `allow_credentials` — whether to allow cookies and authorization headers
- `allow_methods` — which HTTP methods to allow (`["GET", "POST"]` or `["*"]` for all)
- `allow_headers` — which headers the client can send

## Trusted Host Middleware

Protects against HTTP Host header attacks by validating the Host header:

    from fastapi.middleware.trustedhost import TrustedHostMiddleware

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["example.com", "*.example.com"],
    )

## Middleware Execution Order

Middleware is executed in the reverse order of how it is added. The last middleware added is the first to process the request:

    app.add_middleware(MiddlewareA)  # Runs second for request, first for response
    app.add_middleware(MiddlewareB)  # Runs first for request, second for response

This is important when middleware depends on the behavior of other middleware (e.g., logging middleware should be added last so it wraps everything).
