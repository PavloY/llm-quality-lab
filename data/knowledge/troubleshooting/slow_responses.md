# Slow Responses in FastAPI

## Async vs Sync: The Number One Performance Killer

FastAPI runs on an async event loop (uvicorn + asyncio). If you block the event loop with synchronous code, ALL requests wait. This is the most common cause of slow responses.

**Bad — blocks the event loop:**

    import time

    @app.get("/slow")
    async def slow_endpoint():
        time.sleep(5)  # Blocks the entire server for 5 seconds!
        return {"status": "done"}

**Good — use async sleep or run in threadpool:**

    import asyncio

    @app.get("/fast")
    async def fast_endpoint():
        await asyncio.sleep(5)  # Non-blocking, other requests proceed
        return {"status": "done"}

**Also good — use sync def (FastAPI runs it in a threadpool automatically):**

    @app.get("/also-fast")
    def sync_endpoint():
        time.sleep(5)  # OK! FastAPI runs sync functions in a threadpool
        return {"status": "done"}

The rule: if your function uses `await`, declare it `async def`. If it does blocking I/O (database, file reads, HTTP calls to external services), either use async libraries or declare it as plain `def` (not `async def`).

## Common Blocking Operations

1. **`requests` library**: Use `httpx` with `AsyncClient` instead.
2. **SQLAlchemy sync engine**: Use `create_async_engine` with `asyncpg`.
3. **File I/O**: Use `aiofiles` for large files, or plain `def` for small reads.
4. **CPU-heavy computation**: Use `run_in_executor` or a background task queue (Celery, ARQ).

## Diagnosing Slow Endpoints

Add timing middleware to find bottlenecks:

    import time

    @app.middleware("http")
    async def timing_middleware(request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        if duration > 1.0:
            print(f"SLOW: {request.method} {request.url.path} took {duration:.3f}s")
        return response

Check uvicorn worker count. Default is 1 worker — for production use:

    uvicorn app.main:app --workers 4
