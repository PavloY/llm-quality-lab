# FastAPI Dependency Injection

## What is Depends()

FastAPI has a built-in dependency injection system using `Depends()`. Dependencies are functions that are executed before your route handler and can provide shared logic like database connections, authentication, pagination, and more.

Basic example:

    from fastapi import Depends, FastAPI

    app = FastAPI()

    def common_parameters(skip: int = 0, limit: int = 100):
        return {"skip": skip, "limit": limit}

    @app.get("/items")
    def read_items(commons: dict = Depends(common_parameters)):
        return {"params": commons}

When a request hits `/items?skip=10&limit=50`, FastAPI first calls `common_parameters(skip=10, limit=50)`, then passes the result to `read_items` as the `commons` argument.

## Class-Based Dependencies

You can use classes as dependencies. FastAPI will instantiate them and inject the instance. This is useful when your dependency has configuration or state.

    class Pagination:
        def __init__(self, skip: int = 0, limit: int = 100):
            self.skip = skip
            self.limit = limit

    @app.get("/users")
    def list_users(pagination: Pagination = Depends(Pagination)):
        return {"skip": pagination.skip, "limit": pagination.limit}

The class constructor parameters are extracted from the request query parameters automatically.

## Nested Dependencies

Dependencies can depend on other dependencies, forming a dependency tree. FastAPI resolves the entire tree automatically.

    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def get_current_user(db=Depends(get_db)):
        user = db.query(User).first()
        return user

    @app.get("/profile")
    def read_profile(user=Depends(get_current_user)):
        return {"username": user.name}

Notice the `yield` keyword in `get_db()` — this creates a context-managed dependency. Code after `yield` runs after the response is sent, ensuring the database session is always closed.

## Global Dependencies

You can add dependencies to the entire application or to specific routers using the `dependencies` parameter:

    app = FastAPI(dependencies=[Depends(verify_api_key)])

    router = APIRouter(dependencies=[Depends(check_admin_role)])

These dependencies run for every route in the app or router but do not inject their return value into route functions. They are typically used for authentication and authorization checks.
