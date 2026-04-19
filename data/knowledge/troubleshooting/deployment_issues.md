# FastAPI Deployment Issues

## Uvicorn Configuration

**Development** (auto-reload, single worker):

    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

**Production** (multiple workers, no reload):

    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

Or use Gunicorn with uvicorn workers for better process management:

    gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

Common mistakes:
- `--reload` in production: wastes resources watching files.
- `--workers 1` (default): one worker handles all requests sequentially.
- Forgetting `--host 0.0.0.0`: default is `127.0.0.1`, which is not accessible from outside the container.

## Docker Pitfalls

**Problem: Container exits immediately.**
Check if your app crashes on startup. Run interactively to see errors:

    docker run -it myapp bash
    python -c "from app.main import app"

**Problem: Cannot connect to the database / other services.**
Inside Docker, `localhost` refers to the container itself, not your host machine. Use the service name from `docker-compose.yaml` or `host.docker.internal`.

## Environment Variables

**Problem: Settings are empty or wrong in production.**

1. Pass env vars via Docker:

        docker run -e LLM_API_KEY=sk-xxx -e QDRANT_HOST=qdrant myapp

2. With docker-compose:

        services:
          app:
            env_file: .env

3. Never hardcode secrets in code or Dockerfiles. Use environment variables or a secrets manager.

## Health Check

Always add a health endpoint for orchestrators (Kubernetes, Docker Compose):

    @app.get("/healthz")
    def health_check():
        return {"status": "ok"}
