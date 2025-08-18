"""
Initialize 
uv add clerk-sdk
uv add python-jose cryptography httpx cachetools

Introduced Clerk Auth as well here 

Get a clerk account 

These in the .env file 

NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=
CLERK_SECRET_KEY=
CLERK_ISSUER=
JWKS_URL=

jwt token will be validated using jwks key from jwks_url and get userid and details.

You can test using inspector. Enter Bearer token 

Getitng Bearer token from clerk 

1. export CLERK_SECRET_KEY=sk_test_**
2. Create a session id from this
curl -X POST https://api.clerk.com/v1/sessions \
  -H "Authorization: Bearer $CLERK_SECRET_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id”:”your clerk user id”}’
3. Using Session Id, get a jwt token
curl -X POST "https://api.clerk.com/v1/sessions/<your-session-id >/tokens" \
  -H "Authorization: Bearer $CLERK_SECRET_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{}'
"""

from fastmcp import FastMCP
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import os, time, json

from cachetools import TTLCache
from jose import jwt, jwk
from jose.exceptions import ExpiredSignatureError, JWTClaimsError, JWKError, JWTError
from jose.utils import base64url_decode
from jose.backends.cryptography_backend import CryptographyRSAKey
import httpx


load_dotenv()
CLERK_ISSUER = os.getenv("CLERK_ISSUER", "").rstrip("/")
JWKS_URL=os.getenv("JWKS_URL","")


_jwks_cache = TTLCache(maxsize=1, ttl=3600)

async def _get_jwks():
    jwks = _jwks_cache.get("jwks")
    if jwks is None:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(JWKS_URL)
            resp.raise_for_status()
            jwks = resp.json()
        _jwks_cache["jwks"] = jwks
    return jwks

def _select_key_from_jwks(token: str, jwks: dict):
    header = jwt.get_unverified_header(token)
    kid = header.get("kid")
    if not kid:
        raise JWKError("Token header missing 'kid'.")
    keys = jwks.get("keys") or []
    for k in keys:
        if k.get("kid") == kid:
            # Convert JWK to a key object usable by python-jose
            key_obj = jwk.construct(k, algorithm="RS256")
            return key_obj.to_pem().decode("utf-8")
    raise JWKError(f"No matching JWK for kid={kid}")

class ClerkJWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Allow health & CORS preflight without auth
        if request.method == "OPTIONS" or request.url.path in ("/", "/health"):
            return await call_next(request)

        auth = request.headers.get("authorization", "")
        if not auth.startswith("Bearer "):
            return JSONResponse({"error": "Missing/invalid Authorization header"}, 401)
        token = auth.split(" ", 1)[1].strip()

        try:
            jwks = await _get_jwks()
            key  = _select_key_from_jwks(token, jwks)
            # jose can take the JWKS directly via the 'key' parameter using algorithms=["RS256"]
            # We’ll verify iss, exp/nbf are checked by default.
            claims = jwt.decode(
                token,
                key,                      # JWKS dict
                algorithms=["RS256"],
                issuer=CLERK_ISSUER,
            )
            # Attach identity for downstream handlers/tools
            request.state.clerk_claims = claims      # full claims
            request.state.user_id = claims.get("sub")
            request.state.session_id = claims.get("sid")

        except Exception as e:
            return JSONResponse({"error": f"Invalid token: {str(e)}"}, status_code=401)

        return await call_next(request)


mcp = FastMCP("Simple tool")

@mcp.tool()
async def get_current_time() -> str:
    """Get the current time in a human-readable format."""
    return f"Current time: {time.strftime('%Y-%m-%d %H:%M:%S')}"

@mcp.tool()
async def echo_message(message: str) -> str:
    """Echo back the provided message.
    
    Args:
        message: The message to echo back
    """
    return f"Echo: {message}"

if __name__ == "__main__":
    mcp.run(
        transport='http',
        host='127.0.0.1',
        port=8000,
        middleware = [
            Middleware(
                CORSMiddleware,
                allow_origins=['*'],
                allow_credentials=True,
                allow_methods=['*'],
                allow_headers=['*'],
            ),
            Middleware(ClerkJWTMiddleware)
        ]


    )