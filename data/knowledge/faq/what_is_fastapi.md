# What is FastAPI

## Overview

FastAPI is a modern, high-performance web framework for building APIs with Python 3.7+ based on standard Python type hints. Created by Sebastian Ramirez in 2018, it has quickly become one of the most popular Python web frameworks.

Key selling points:
- **Fast**: On par with NodeJS and Go in benchmarks (thanks to Starlette and Pydantic).
- **Fast to code**: Type hints drive automatic validation, serialization, and documentation.
- **Automatic docs**: Swagger UI at `/docs` and ReDoc at `/redoc` are generated automatically.
- **Standards-based**: Built on OpenAPI (formerly Swagger) and JSON Schema.

## When to Use FastAPI

**Good fit:**
- REST APIs and microservices
- Machine learning model serving (async support handles concurrent prediction requests well)
- Real-time applications with WebSockets
- Projects where automatic data validation saves development time
- Teams that value type safety and auto-generated documentation

**Not the best fit:**
- Server-side rendered HTML websites (use Django or Flask with templates instead)
- Simple scripts that do not need an HTTP API
- Projects requiring a large ecosystem of third-party plugins (Django has more mature extensions)

## Comparison with Flask

Flask is synchronous by default, minimal, and has no built-in validation. FastAPI is async-first, includes Pydantic validation, and generates OpenAPI docs automatically. Flask is better for simple prototypes; FastAPI scales better for production APIs with complex data models.

## Comparison with Django REST Framework

Django DRF comes with an ORM, admin panel, authentication, and dozens of built-in features. FastAPI is lighter and faster but you have to pick your own ORM, auth library, etc. Choose Django DRF for full-featured web applications; FastAPI for high-performance APIs and microservices.
