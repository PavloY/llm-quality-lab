# Async vs Sync in FastAPI

## When to Use async def

Use `async def` when your function needs to `await` something — an async database query, an async HTTP call, an async file read, or any other coroutine.

    @app.get("/users")
    async def get_users():
        users = await db.fetch_all("SELECT * FROM users")  # async DB call
        return users

The `await` keyword pauses this function without blocking the event loop, so other requests can be processed while waiting for the database.

## When to Use Plain def

Use regular `def` (not `async def`) when your function does synchronous blocking I/O — reading a file with standard `open()`, calling an external API with `requests`, or running CPU-heavy code.

    @app.get("/report")
    def generate_report():
        data = requests.get("https://api.example.com/data").json()  # Sync HTTP call
        return process(data)

FastAPI automatically runs `def` functions in a separate threadpool, so they do not block the event loop. This is safe and works well for most use cases.

## The Dangerous Mistake

**Never do blocking I/O inside `async def`:**

    @app.get("/bad")
    async def bad_endpoint():
        data = requests.get("https://slow-api.com/data")  # BLOCKS the event loop!
        return data.json()

This blocks the entire event loop. All other requests wait until this one finishes. Either use `async def` with an async HTTP client like `httpx`, or use plain `def`.

## Performance Implications

- **Async endpoints with async I/O**: Best performance, handles thousands of concurrent connections.
- **Sync endpoints (plain def)**: Good performance, limited by threadpool size (default 40 threads).
- **Async endpoints with sync I/O**: Worst performance, blocks everything.

## Rule of Thumb

If in doubt, use plain `def`. FastAPI handles it safely. Only use `async def` when you have actual async operations to `await`.
