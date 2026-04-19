# Import Errors in FastAPI Projects

## Circular Import: ImportError or AttributeError

The most confusing error in Python projects. You have `models.py` importing from `database.py`, and `database.py` importing from `models.py`. Python cannot resolve this loop and throws `ImportError: cannot import name 'X' from partially initialized module`.

**How to fix:**

1. **Move the import inside the function** (lazy import):

        def get_user():
            from app.models import User  # Import here, not at top of file
            return User.query.first()

2. **Use TYPE_CHECKING block** (for type hints only):

        from __future__ import annotations
        from typing import TYPE_CHECKING

        if TYPE_CHECKING:
            from app.models import User

3. **Restructure**: Create a third module that both can import from. Usually move shared types/base classes to a `base.py` or `types.py`.

## ModuleNotFoundError: No module named 'app'

This means Python cannot find your `app` package. Common causes:

1. **Missing `__init__.py`**: Every directory that you import from needs an `__init__.py` file (even if it is empty).
2. **Wrong working directory**: Run your app from the project root, not from inside `app/`.
3. **Module not installed**: If your project is a package, install it with `pip install -e .`.
4. **PYTHONPATH not set**: Add the project root to PYTHONPATH:

        export PYTHONPATH="${PYTHONPATH}:$(pwd)"

## Common Project Structure Issues

**Bad structure** (everything flat):

    main.py
    models.py
    config.py

**Good structure** (proper package):

    project/
    ├── app/
    │   ├── __init__.py
    │   ├── main.py
    │   ├── models.py
    │   └── config.py
    ├── tests/
    └── requirements.txt

Run from `project/` directory: `uvicorn app.main:app`.

## FastAPI-Specific Import Gotcha

If you use `APIRouter` in separate files, import the router AFTER defining routes:

    # app/main.py
    from app.routes.users import router as users_router  # Must be after routes are defined
    app.include_router(users_router)
