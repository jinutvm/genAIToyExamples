# Install Prerequisties using uv

- uv init . 
- uv add fastmcp dotenv

# Simple MCP server

### I01_simple.py

- Create 2 simple tools
- Run the MCP server
- Test using inspector
- Use ngrok for https 
- Connect to Claude Code
- Test using chat

### I02_addAuth.py

- Added clerk authentication 
####  Initialize 
        uv add clerk-sdk
        uv add python-jose cryptography httpx cachetools

####    Introduced Clerk Auth as well here 

#####    Get a clerk account 

#####    These in the .env file 

        NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=
        CLERK_SECRET_KEY=
        CLERK_ISSUER=
        JWKS_URL=

    jwt token will be validated using jwks key from jwks_url and get userid and details.

    You can test using inspector. Enter Bearer token 

#####    Getitng Bearer token from clerk 

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