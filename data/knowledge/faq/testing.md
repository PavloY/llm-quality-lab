# Testing FastAPI Applications

## TestClient Basics

FastAPI provides a `TestClient` (built on `httpx`) for testing your API without starting a real server:

    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)

    def test_read_root():
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello, World!"}

    def test_create_item():
        response = client.post("/items", json={"name": "Widget", "price": 9.99})
        assert response.status_code == 200
        assert response.json()["name"] == "Widget"

The TestClient handles the ASGI protocol internally — no real HTTP connection is made, so tests are fast.

## Pytest Fixtures for FastAPI

Use fixtures to set up the test client and shared dependencies:

    import pytest
    from fastapi.testclient import TestClient
    from app.main import app

    @pytest.fixture
    def client():
        return TestClient(app)

    @pytest.fixture
    def test_db():
        """Override the database dependency with a test database."""
        engine = create_engine("sqlite:///./test.db")
        Base.metadata.create_all(bind=engine)
        TestSession = sessionmaker(bind=engine)
        db = TestSession()
        try:
            yield db
        finally:
            db.close()
            Base.metadata.drop_all(bind=engine)

## Dependency Overrides

FastAPI lets you replace dependencies during testing. This is powerful for mocking external services:

    from app.main import app
    from app.dependencies import get_current_user

    def override_get_current_user():
        return {"username": "testuser", "role": "admin"}

    app.dependency_overrides[get_current_user] = override_get_current_user

    client = TestClient(app)
    response = client.get("/protected")
    assert response.status_code == 200

    # Clean up
    app.dependency_overrides.clear()

## Testing Async Endpoints

For async endpoints, use `pytest-asyncio` and `httpx.AsyncClient`:

    import pytest
    from httpx import AsyncClient, ASGITransport
    from app.main import app

    @pytest.mark.asyncio
    async def test_async_endpoint():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/async-endpoint")
            assert response.status_code == 200
