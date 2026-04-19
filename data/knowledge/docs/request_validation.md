# FastAPI Request Validation

## Pydantic Models for Request Body

FastAPI uses Pydantic models to validate request bodies. When you declare a function parameter with a Pydantic model type, FastAPI automatically parses the JSON request body and validates it against the model.

    from fastapi import FastAPI
    from pydantic import BaseModel

    app = FastAPI()

    class Item(BaseModel):
        name: str
        price: float
        description: str | None = None
        is_offer: bool = False

    @app.post("/items")
    def create_item(item: Item):
        return {"item_name": item.name, "item_price": item.price}

If the client sends invalid data (e.g., a string for `price`), FastAPI automatically returns a 422 Unprocessable Entity response with detailed error messages explaining what went wrong.

## Field Validation with Pydantic

Pydantic provides `Field()` for adding constraints and metadata to model fields:

    from pydantic import BaseModel, Field

    class Item(BaseModel):
        name: str = Field(min_length=1, max_length=100, description="The item name")
        price: float = Field(gt=0, description="Price must be greater than zero")
        quantity: int = Field(ge=0, le=10000, description="Stock quantity")
        tags: list[str] = Field(default_factory=list, max_length=10)

Common Field constraints:
- `gt`, `ge`, `lt`, `le` — greater than, greater or equal, less than, less or equal (for numbers)
- `min_length`, `max_length` — for strings and lists
- `pattern` — regex pattern for strings
- `default_factory` — callable that produces the default value

## Query Parameter Validation

For query parameters, use FastAPI's `Query()` to add validation:

    from fastapi import Query

    @app.get("/items")
    def list_items(
        q: str | None = Query(None, min_length=3, max_length=50),
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
    ):
        return {"q": q, "skip": skip, "limit": limit}

## Nested Models

Pydantic models can be nested to validate complex data structures:

    class Address(BaseModel):
        street: str
        city: str
        zip_code: str = Field(pattern=r"^\d{5}$")

    class User(BaseModel):
        name: str
        email: str
        addresses: list[Address] = []

    @app.post("/users")
    def create_user(user: User):
        return {"user": user.name, "address_count": len(user.addresses)}

FastAPI validates the entire nested structure recursively and returns clear error messages pointing to the exact location of the validation failure (e.g., `body -> addresses -> 0 -> zip_code`).

## Custom Validators

Use Pydantic's `field_validator` for custom validation logic:

    from pydantic import BaseModel, field_validator

    class User(BaseModel):
        name: str
        email: str

        @field_validator("email")
        @classmethod
        def validate_email(cls, v: str) -> str:
            if "@" not in v:
                raise ValueError("Invalid email address")
            return v.lower()

The validator runs during model creation and can transform the value (like lowercasing the email) or raise `ValueError` to reject it.
