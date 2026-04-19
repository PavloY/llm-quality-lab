# CORS Issues in FastAPI

## Symptoms

You see errors like these in the browser console:

    Access to fetch at 'http://localhost:8000/api' from origin 'http://localhost:3000'
    has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present.

Or for preflight requests:

    Response to preflight request doesn't pass access control check:
    No 'Access-Control-Allow-Origin' header.

This happens when your frontend (e.g., React on port 3000) makes requests to your FastAPI backend (port 8000). Browsers enforce Same-Origin Policy and block cross-origin requests unless the server explicitly allows them via CORS headers.

## The Fix: CORSMiddleware

    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

## Common Mistakes

1. **Adding middleware AFTER routes**: Middleware must be added before route definitions or it might not work for all routes. Best practice — add it right after `app = FastAPI()`.
2. **Using `allow_origins=["*"]` with `allow_credentials=True`**: This combination is forbidden by the CORS spec. Either list specific origins or set `allow_credentials=False`.
3. **Forgetting OPTIONS method**: Preflight requests use OPTIONS. If you restrict `allow_methods`, include OPTIONS.
4. **Proxy confusion**: If you use nginx or another reverse proxy, CORS might need to be configured there instead of (or in addition to) FastAPI.
5. **Caching preflight**: Browsers cache preflight responses. After changing CORS config, clear browser cache or use incognito mode to test.

## Testing CORS

Test with curl to see the actual headers:

    curl -X OPTIONS http://localhost:8000/api \
      -H "Origin: http://localhost:3000" \
      -H "Access-Control-Request-Method: POST" \
      -v

Look for `Access-Control-Allow-Origin` in the response headers.
