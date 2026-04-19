# Database Integration with FastAPI

## SQLAlchemy Setup

The most popular ORM for FastAPI. Basic synchronous setup:

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, DeclarativeBase

    SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    class Base(DeclarativeBase):
        pass

Use a dependency to manage database sessions:

    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    @app.get("/users")
    def get_users(db: Session = Depends(get_db)):
        return db.query(User).all()

The `yield` ensures the session is closed after the request, even if an error occurs.

## Async Database with asyncpg

For high-performance async access, use SQLAlchemy 2.0 with asyncpg:

    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

    engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async def get_db():
        async with async_session() as session:
            yield session

    @app.get("/users")
    async def get_users(db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(User))
        return result.scalars().all()

## Migrations with Alembic

Alembic manages database schema changes (migrations). Setup:

    pip install alembic
    alembic init alembic

Edit `alembic/env.py` to point to your Base metadata:

    from app.models import Base
    target_metadata = Base.metadata

Create and run migrations:

    alembic revision --autogenerate -m "add users table"
    alembic upgrade head

Always review auto-generated migrations before applying them — Alembic sometimes misses or misinterprets changes (especially for renamed columns or complex constraints).
