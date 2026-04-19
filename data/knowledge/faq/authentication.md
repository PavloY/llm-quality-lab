# Authentication in FastAPI

## OAuth2 with Password Flow

FastAPI has built-in support for OAuth2. The simplest approach is the password flow — the client sends username and password, the server returns a token.

    from fastapi import Depends, FastAPI, HTTPException
    from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

    app = FastAPI()
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    @app.post("/token")
    def login(form_data: OAuth2PasswordRequestForm = Depends()):
        if form_data.username != "admin" or form_data.password != "secret":
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return {"access_token": "fake-token", "token_type": "bearer"}

    @app.get("/protected")
    def protected_route(token: str = Depends(oauth2_scheme)):
        return {"message": "You have access", "token": token}

The `OAuth2PasswordBearer` dependency extracts the token from the `Authorization: Bearer <token>` header automatically.

## JWT Tokens

For production, use JWT (JSON Web Tokens) instead of fake tokens. Install `python-jose`:

    pip install python-jose[cryptography]

Create and verify tokens:

    from jose import JWTError, jwt
    from datetime import datetime, timedelta

    SECRET_KEY = "your-secret-key"
    ALGORITHM = "HS256"

    def create_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):
        to_encode = data.copy()
        to_encode["exp"] = datetime.utcnow() + expires_delta
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def verify_token(token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

## Adding Auth to All Routes

Use a dependency on the router or app level:

    from fastapi import APIRouter

    router = APIRouter(dependencies=[Depends(get_current_user)])

    @router.get("/dashboard")
    def dashboard():
        return {"page": "dashboard"}

Every route on this router will require authentication.
