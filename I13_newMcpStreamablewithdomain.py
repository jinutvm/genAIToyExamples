"""Enhanced MCP server with weather and forecast functionality."""

import argparse
import json
import time
import os
import secrets
import hashlib
import base64
from typing import Any, Dict, Optional
import uvicorn
import httpx
from mcp.server.fastmcp import FastMCP
from starlette.responses import JSONResponse, RedirectResponse
from starlette.requests import Request
from urllib.parse import urlencode

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Install with: pip install python-dotenv")

mcp = FastMCP(name="weather-test-server", json_response=False, stateless_http=False)

# Weather API configuration
OPENWEATHER_API_BASE = "https://api.openweathermap.org/data/2.5"
GEO_API_BASE = "https://api.openweathermap.org/geo/1.0"
API_KEY = os.getenv("OPENWEATHER_API_KEY", "demo")  # Get from environment variable

# OAuth 2.0 configuration
OAUTH_CLIENT_ID = os.getenv("OAUTH_CLIENT_ID", "weather-mcp-client")
OAUTH_CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET", "demo-secret")
OAUTH_REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI", "http://localhost:8124/oauth/callback")
JWT_SECRET = os.getenv("JWT_SECRET", "demo-jwt-secret")

# In-memory storage for OAuth state and tokens (use Redis/DB in production)
oauth_states = {}
auth_codes = {}
access_tokens = {}
refresh_tokens = {}

async def make_weather_request(url: str) -> Dict[str, Any] | None:
    """Make a request to OpenWeatherMap API with error handling."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            if response.status_code == 401:
                return {"error": "Invalid API key. Please set a valid OpenWeatherMap API key."}
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            return {"error": "Request timeout"}
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}

async def get_coordinates(city: str) -> Optional[tuple]:
    """Get latitude and longitude for a city."""
    url = f"{GEO_API_BASE}/direct?q={city}&limit=1&appid={API_KEY}"
    data = await make_weather_request(url)
    
    if not data or "error" in data or not data:
        return None
    
    if len(data) > 0:
        return data[0]["lat"], data[0]["lon"]
    return None

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

@mcp.tool()
async def add_numbers(a: float, b: float) -> str:
    """Add two numbers together.
    
    Args:
        a: First number
        b: Second number
    """
    result = a + b
    return f"{a} + {b} = {result}"

@mcp.tool()
async def get_weather(city: str) -> str:
    """Get current weather information for a city.
    
    Args:
        city: Name of the city (e.g., 'London', 'New York', 'Tokyo')
    """
    coords = await get_coordinates(city)
    if not coords:
        return f"Could not find coordinates for city: {city}"
    
    lat, lon = coords
    url = f"{OPENWEATHER_API_BASE}/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    data = await make_weather_request(url)
    
    if not data or "error" in data:
        return f"Error fetching weather: {data.get('error', 'Unknown error')}"
    
    weather = data["weather"][0]
    main = data["main"]
    wind = data.get("wind", {})
    
    return f"""Weather in {city}:
Temperature: {main['temp']}�C (feels like {main['feels_like']}�C)
Condition: {weather['main']} - {weather['description']}
Humidity: {main['humidity']}%
Pressure: {main['pressure']} hPa
Wind: {wind.get('speed', 'N/A')} m/s
Visibility: {data.get('visibility', 'N/A')} meters"""

@mcp.tool()
async def get_forecast(city: str, days: int = 3) -> str:
    """Get weather forecast for a city.
    
    Args:
        city: Name of the city (e.g., 'London', 'New York', 'Tokyo')
        days: Number of days to forecast (1-5, default: 3)
    """
    if days < 1 or days > 5:
        return "Days must be between 1 and 5"
    
    coords = await get_coordinates(city)
    if not coords:
        return f"Could not find coordinates for city: {city}"
    
    lat, lon = coords
    url = f"{OPENWEATHER_API_BASE}/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    data = await make_weather_request(url)
    
    if not data or "error" in data:
        return f"Error fetching forecast: {data.get('error', 'Unknown error')}"
    
    forecasts = []
    count = 0
    for item in data["list"]:
        if count >= days * 8:  # 8 forecasts per day (3-hour intervals)
            break
        
        dt = item["dt_txt"]
        weather = item["weather"][0]
        main = item["main"]
        
        forecast = f"{dt}: {main['temp']}�C, {weather['description']}"
        forecasts.append(forecast)
        count += 1
    
    return f"Forecast for {city} (next {days} days):\n" + "\n".join(forecasts[:days*2])  # Show 2 times per day

@mcp.tool()
async def get_weather_alerts(city: str) -> str:
    """Get weather alerts for a city (if available).
    
    Args:
        city: Name of the city
    """
    coords = await get_coordinates(city)
    if not coords:
        return f"Could not find coordinates for city: {city}"
    
    lat, lon = coords
    url = f"{OPENWEATHER_API_BASE}/weather?lat={lat}&lon={lon}&appid={API_KEY}"
    data = await make_weather_request(url)
    
    if not data or "error" in data:
        return f"Error fetching weather data: {data.get('error', 'Unknown error')}"
    
    # Check for extreme weather conditions
    alerts = []
    weather = data["weather"][0]["main"].lower()
    temp = data["main"]["temp"]
    wind_speed = data.get("wind", {}).get("speed", 0)
    
    if "storm" in weather or "thunderstorm" in weather:
        alerts.append("� Thunderstorm alert")
    if temp > 35:
        alerts.append("<! High temperature warning")
    elif temp < -10:
        alerts.append("D Extreme cold warning")
    if wind_speed > 15:
        alerts.append("=� High wind warning")
    
    if alerts:
        return f"Weather alerts for {city}:\n" + "\n".join(alerts)
    else:
        return f"No weather alerts for {city}"

@mcp.tool()
async def compare_cities_weather(city1: str, city2: str) -> str:
    """Compare weather between two cities.
    
    Args:
        city1: First city name
        city2: Second city name
    """
    # Get weather for both cities
    coords1 = await get_coordinates(city1)
    coords2 = await get_coordinates(city2)
    
    if not coords1:
        return f"Could not find coordinates for city: {city1}"
    if not coords2:
        return f"Could not find coordinates for city: {city2}"
    
    lat1, lon1 = coords1
    lat2, lon2 = coords2
    
    url1 = f"{OPENWEATHER_API_BASE}/weather?lat={lat1}&lon={lon1}&appid={API_KEY}&units=metric"
    url2 = f"{OPENWEATHER_API_BASE}/weather?lat={lat2}&lon={lon2}&appid={API_KEY}&units=metric"
    
    data1 = await make_weather_request(url1)
    data2 = await make_weather_request(url2)
    
    if not data1 or "error" in data1:
        return f"Error fetching weather for {city1}"
    if not data2 or "error" in data2:
        return f"Error fetching weather for {city2}"
    
    temp1 = data1["main"]["temp"]
    temp2 = data2["main"]["temp"]
    desc1 = data1["weather"][0]["description"]
    desc2 = data2["weather"][0]["description"]
    
    temp_diff = abs(temp1 - temp2)
    warmer_city = city1 if temp1 > temp2 else city2
    
    return f"""Weather comparison:
{city1}: {temp1}�C, {desc1}
{city2}: {temp2}�C, {desc2}

{warmer_city} is warmer by {temp_diff:.1f}�C"""

@mcp.tool()
async def get_server_info() -> str:
    """Get information about this MCP server."""
    return json.dumps({
        "name": "weather-test-server",
        "version": "1.0.0",
        "description": "MCP server with weather and forecast functionality",
        "tools": [
            "get_current_time", 
            "echo_message", 
            "add_numbers", 
            "get_weather", 
            "get_forecast", 
            "get_weather_alerts",
            "compare_cities_weather",
            "get_server_info"
        ],
        "note": "Weather data requires valid OpenWeatherMap API key",
        "api_key_status": "configured" if API_KEY != "demo" else "demo_mode"
    }, indent=2)

@mcp.tool()
async def health_check() -> str:
    """Health check endpoint for server monitoring."""
    return json.dumps({
        "status": "healthy",
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
        "server": "weather-test-server",
        "api_available": API_KEY != "demo"
    })

# Add health endpoint to FastMCP app
app = mcp.streamable_http_app()

@app.route("/health")
async def health_endpoint(request):
    """HTTP health check endpoint."""
    return JSONResponse({
        "status": "healthy",
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
        "server": "weather-test-server",
        "api_available": API_KEY != "demo"
    })

@app.route("/mcp", methods=["GET", "POST"])
async def mcp_endpoint(request: Request):
    """MCP protocol endpoint - handles JSON-RPC requests."""
    if request.method == "GET":
        # Handle GET request with query parameters
        query_params = dict(request.query_params)
        
        # Return server capabilities
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "protocolVersion": "2025-06-18",
                "capabilities": {
                    "tools": {
                        "listChanged": False
                    }
                },
                "serverInfo": {
                    "name": "weather-test-server",
                    "version": "1.0.0",
                    "description": "Enhanced MCP weather server with forecast functionality"
                },
                "tools": [
                    {
                        "name": "get_current_time",
                        "description": "Get the current time in a human-readable format",
                        "inputSchema": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    },
                    {
                        "name": "echo_message",
                        "description": "Echo back the provided message",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "message": {
                                    "type": "string",
                                    "description": "The message to echo back"
                                }
                            },
                            "required": ["message"]
                        }
                    },
                    {
                        "name": "add_numbers",
                        "description": "Add two numbers together",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "a": {
                                    "type": "number",
                                    "description": "First number"
                                },
                                "b": {
                                    "type": "number",
                                    "description": "Second number"
                                }
                            },
                            "required": ["a", "b"]
                        }
                    },
                    {
                        "name": "get_weather",
                        "description": "Get current weather information for a city",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "city": {
                                    "type": "string",
                                    "description": "Name of the city (e.g., 'London', 'New York', 'Tokyo')"
                                }
                            },
                            "required": ["city"]
                        }
                    },
                    {
                        "name": "get_forecast",
                        "description": "Get weather forecast for a city",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "city": {
                                    "type": "string",
                                    "description": "Name of the city"
                                },
                                "days": {
                                    "type": "integer",
                                    "description": "Number of days to forecast (1-5, default: 3)",
                                    "minimum": 1,
                                    "maximum": 5,
                                    "default": 3
                                }
                            },
                            "required": ["city"]
                        }
                    },
                    {
                        "name": "get_weather_alerts",
                        "description": "Get weather alerts for a city (if available)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "city": {
                                    "type": "string",
                                    "description": "Name of the city"
                                }
                            },
                            "required": ["city"]
                        }
                    },
                    {
                        "name": "compare_cities_weather",
                        "description": "Compare weather between two cities",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "city1": {
                                    "type": "string",
                                    "description": "First city name"
                                },
                                "city2": {
                                    "type": "string",
                                    "description": "Second city name"
                                }
                            },
                            "required": ["city1", "city2"]
                        }
                    },
                    {
                        "name": "get_server_info",
                        "description": "Get information about this MCP server",
                        "inputSchema": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    },
                    {
                        "name": "health_check",
                        "description": "Health check endpoint for server monitoring",
                        "inputSchema": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    }
                ]
            }
        })
    
    elif request.method == "POST":
        # Handle POST request with JSON-RPC
        try:
            data = await request.json()
            print(f"[DEBUG] Raw POST data: {data}")
            method = data.get("method")
            params = data.get("params", {})
            request_id = data.get("id", 1)
            
            # Debug logging
            print(f"[DEBUG] MCP method: {method}, params: {params}, id: {request_id}")
            
            if method == "initialize":
                # Handle MCP initialization
                client_protocol_version = params.get("protocolVersion", "2024-11-05")
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": client_protocol_version,  # Use client's version
                        "capabilities": {
                            "tools": {
                                "listChanged": False
                            }
                        },
                        "serverInfo": {
                            "name": "weather-test-server",
                            "version": "1.0.0",
                            "description": "Enhanced MCP weather server with forecast functionality"
                        }
                    }
                })
            
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                
                # Map tool calls to functions
                tool_functions = {
                    "get_current_time": get_current_time,
                    "echo_message": echo_message,
                    "add_numbers": add_numbers,
                    "get_weather": get_weather,
                    "get_forecast": get_forecast,
                    "get_weather_alerts": get_weather_alerts,
                    "compare_cities_weather": compare_cities_weather,
                    "get_server_info": get_server_info,
                    "health_check": health_check
                }
                
                if tool_name in tool_functions:
                    try:
                        result = await tool_functions[tool_name](**tool_args)
                        return JSONResponse({
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {
                                "content": [
                                    {
                                        "type": "text",
                                        "text": result
                                    }
                                ]
                            }
                        })
                    except Exception as e:
                        return JSONResponse({
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {
                                "code": -32603,
                                "message": f"Tool execution error: {str(e)}"
                            }
                        })
                else:
                    return JSONResponse({
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Tool not found: {tool_name}"
                        }
                    })
            
            elif method == "notifications/initialized":
                # Handle MCP initialization notification (notifications don't have responses)
                # For notifications (no id), return empty response
                if "id" not in data:
                    # This is a notification - return empty response
                    return JSONResponse({})
                else:
                    return JSONResponse({
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {}
                    })
            
            elif method == "tools/list":
                # Return list of available tools
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": [
                            {
                                "name": "get_current_time",
                                "description": "Get the current time in a human-readable format",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {},
                                    "required": []
                                }
                            },
                            {
                                "name": "echo_message",
                                "description": "Echo back the provided message",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "message": {
                                            "type": "string",
                                            "description": "The message to echo back"
                                        }
                                    },
                                    "required": ["message"]
                                }
                            },
                            {
                                "name": "add_numbers",
                                "description": "Add two numbers together",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "a": {
                                            "type": "number",
                                            "description": "First number"
                                        },
                                        "b": {
                                            "type": "number",
                                            "description": "Second number"
                                        }
                                    },
                                    "required": ["a", "b"]
                                }
                            },
                            {
                                "name": "get_weather",
                                "description": "Get current weather information for a city",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "city": {
                                            "type": "string",
                                            "description": "Name of the city (e.g., 'London', 'New York', 'Tokyo')"
                                        }
                                    },
                                    "required": ["city"]
                                }
                            },
                            {
                                "name": "get_forecast",
                                "description": "Get weather forecast for a city",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "city": {
                                            "type": "string",
                                            "description": "Name of the city"
                                        },
                                        "days": {
                                            "type": "integer",
                                            "description": "Number of days to forecast (1-5, default: 3)",
                                            "minimum": 1,
                                            "maximum": 5,
                                            "default": 3
                                        }
                                    },
                                    "required": ["city"]
                                }
                            },
                            {
                                "name": "get_weather_alerts",
                                "description": "Get weather alerts for a city (if available)",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "city": {
                                            "type": "string",
                                            "description": "Name of the city"
                                        }
                                    },
                                    "required": ["city"]
                                }
                            },
                            {
                                "name": "compare_cities_weather",
                                "description": "Compare weather between two cities",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "city1": {
                                            "type": "string",
                                            "description": "First city name"
                                        },
                                        "city2": {
                                            "type": "string",
                                            "description": "Second city name"
                                        }
                                    },
                                    "required": ["city1", "city2"]
                                }
                            },
                            {
                                "name": "get_server_info",
                                "description": "Get information about this MCP server",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {},
                                    "required": []
                                }
                            },
                            {
                                "name": "health_check",
                                "description": "Health check endpoint for server monitoring",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {},
                                    "required": []
                                }
                            }
                        ]
                    }
                })
            
            else:
                print(f"[DEBUG] Unhandled method: {method}")
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                })
                
        except Exception as e:
            print(f"[DEBUG] Exception in POST handler: {str(e)}")
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": 1,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {str(e)}"
                }
            })
    
    else:
        return JSONResponse({
            "error": "Method not allowed"
        }, status_code=405)

# OAuth 2.0 Helper Functions
def generate_code_verifier() -> str:
    """Generate PKCE code verifier."""
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')

def generate_code_challenge(verifier: str) -> str:
    """Generate PKCE code challenge from verifier."""
    digest = hashlib.sha256(verifier.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')

def generate_access_token() -> str:
    """Generate access token."""
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8')

def generate_refresh_token() -> str:
    """Generate refresh token."""
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8')

# OAuth 2.0 Endpoints
@app.route("/.well-known/oauth-authorization-server")
async def oauth_discovery(request):
    """OAuth 2.0 Authorization Server Metadata (RFC 8414)."""
    domain = request.headers.get('host', 'localhost:8124')
    base_url = f"https://{domain}" if ':443' in domain or 'localhost' not in domain else f"http://{domain}"
    
    return JSONResponse({
        "issuer": base_url,
        "authorization_endpoint": f"{base_url}/oauth/authorize",
        "token_endpoint": f"{base_url}/oauth/token",
        "userinfo_endpoint": f"{base_url}/oauth/userinfo",
        "revocation_endpoint": f"{base_url}/oauth/revoke",
        "introspection_endpoint": f"{base_url}/oauth/introspect",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "refresh_token"],
        "code_challenge_methods_supported": ["S256"],
        "scopes_supported": ["weather:read", "weather:forecast", "weather:alerts"],
        "token_endpoint_auth_methods_supported": ["client_secret_post", "client_secret_basic"]
    })

@app.route("/oauth/authorize")
async def oauth_authorize(request: Request):
    """OAuth 2.0 Authorization Endpoint."""
    query_params = dict(request.query_params)
    
    # Extract OAuth parameters
    client_id = query_params.get('client_id')
    redirect_uri = query_params.get('redirect_uri')
    response_type = query_params.get('response_type')
    scope = query_params.get('scope', 'weather:read')
    state = query_params.get('state')
    code_challenge = query_params.get('code_challenge')
    code_challenge_method = query_params.get('code_challenge_method')
    
    # Validate required parameters
    if not client_id or not redirect_uri or response_type != 'code':
        return JSONResponse({
            "error": "invalid_request",
            "error_description": "Missing or invalid required parameters"
        }, status_code=400)
    
    # Validate client_id
    if client_id != OAUTH_CLIENT_ID:
        return JSONResponse({
            "error": "unauthorized_client",
            "error_description": "Invalid client_id"
        }, status_code=400)
    
    # Generate authorization code
    auth_code = secrets.token_urlsafe(32)
    
    # Store authorization code with associated data
    auth_codes[auth_code] = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "code_challenge": code_challenge,
        "code_challenge_method": code_challenge_method,
        "expires_at": time.time() + 600,  # 10 minutes
        "user_id": "demo-user"  # In production, get from authenticated user
    }
    
    # Redirect with authorization code
    callback_params = {
        "code": auth_code,
        "state": state
    } if state else {"code": auth_code}
    
    callback_url = f"{redirect_uri}?{urlencode(callback_params)}"
    return RedirectResponse(url=callback_url)

@app.route("/oauth/token", methods=["POST"])
async def oauth_token(request: Request):
    """OAuth 2.0 Token Endpoint."""
    try:
        # Parse form data
        form_data = await request.form()
        
        grant_type = form_data.get('grant_type')
        
        if grant_type == 'authorization_code':
            # Authorization Code Grant
            code = form_data.get('code')
            client_id = form_data.get('client_id')
            client_secret = form_data.get('client_secret')
            redirect_uri = form_data.get('redirect_uri')
            code_verifier = form_data.get('code_verifier')
            
            # Validate authorization code
            if not code or code not in auth_codes:
                return JSONResponse({
                    "error": "invalid_grant",
                    "error_description": "Invalid or expired authorization code"
                }, status_code=400)
            
            code_data = auth_codes[code]
            
            # Check expiration
            if time.time() > code_data['expires_at']:
                del auth_codes[code]
                return JSONResponse({
                    "error": "invalid_grant",
                    "error_description": "Authorization code expired"
                }, status_code=400)
            
            # Validate client credentials
            if client_id != OAUTH_CLIENT_ID or client_secret != OAUTH_CLIENT_SECRET:
                return JSONResponse({
                    "error": "invalid_client",
                    "error_description": "Invalid client credentials"
                }, status_code=401)
            
            # Validate PKCE if used
            if code_data.get('code_challenge'):
                if not code_verifier:
                    return JSONResponse({
                        "error": "invalid_request",
                        "error_description": "Code verifier required"
                    }, status_code=400)
                
                expected_challenge = generate_code_challenge(code_verifier)
                if expected_challenge != code_data['code_challenge']:
                    return JSONResponse({
                        "error": "invalid_grant",
                        "error_description": "Invalid code verifier"
                    }, status_code=400)
            
            # Generate tokens
            access_token = generate_access_token()
            refresh_token = generate_refresh_token()
            
            # Store tokens
            access_tokens[access_token] = {
                "user_id": code_data['user_id'],
                "client_id": client_id,
                "scope": code_data['scope'],
                "expires_at": time.time() + 3600  # 1 hour
            }
            
            refresh_tokens[refresh_token] = {
                "user_id": code_data['user_id'],
                "client_id": client_id,
                "scope": code_data['scope'],
                "access_token": access_token
            }
            
            # Clean up authorization code
            del auth_codes[code]
            
            return JSONResponse({
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_in": 3600,
                "refresh_token": refresh_token,
                "scope": code_data['scope']
            })
            
        elif grant_type == 'refresh_token':
            # Refresh Token Grant
            refresh_token = form_data.get('refresh_token')
            client_id = form_data.get('client_id')
            client_secret = form_data.get('client_secret')
            
            # Validate refresh token
            if not refresh_token or refresh_token not in refresh_tokens:
                return JSONResponse({
                    "error": "invalid_grant",
                    "error_description": "Invalid refresh token"
                }, status_code=400)
            
            # Validate client credentials
            if client_id != OAUTH_CLIENT_ID or client_secret != OAUTH_CLIENT_SECRET:
                return JSONResponse({
                    "error": "invalid_client",
                    "error_description": "Invalid client credentials"
                }, status_code=401)
            
            token_data = refresh_tokens[refresh_token]
            
            # Revoke old access token
            old_access_token = token_data['access_token']
            if old_access_token in access_tokens:
                del access_tokens[old_access_token]
            
            # Generate new access token
            new_access_token = generate_access_token()
            
            # Store new access token
            access_tokens[new_access_token] = {
                "user_id": token_data['user_id'],
                "client_id": client_id,
                "scope": token_data['scope'],
                "expires_at": time.time() + 3600  # 1 hour
            }
            
            # Update refresh token data
            refresh_tokens[refresh_token]['access_token'] = new_access_token
            
            return JSONResponse({
                "access_token": new_access_token,
                "token_type": "Bearer",
                "expires_in": 3600,
                "scope": token_data['scope']
            })
            
        else:
            return JSONResponse({
                "error": "unsupported_grant_type",
                "error_description": "Grant type not supported"
            }, status_code=400)
            
    except Exception as e:
        return JSONResponse({
            "error": "server_error",
            "error_description": f"Internal server error: {str(e)}"
        }, status_code=500)

@app.route("/oauth/userinfo")
async def oauth_userinfo(request: Request):
    """OAuth 2.0 UserInfo Endpoint."""
    # Extract Bearer token
    authorization = request.headers.get('authorization')
    if not authorization or not authorization.startswith('Bearer '):
        return JSONResponse({
            "error": "invalid_token",
            "error_description": "Missing or invalid authorization header"
        }, status_code=401)
    
    access_token = authorization[7:]  # Remove 'Bearer ' prefix
    
    # Validate access token
    if access_token not in access_tokens:
        return JSONResponse({
            "error": "invalid_token",
            "error_description": "Invalid access token"
        }, status_code=401)
    
    token_data = access_tokens[access_token]
    
    # Check expiration
    if time.time() > token_data['expires_at']:
        del access_tokens[access_token]
        return JSONResponse({
            "error": "invalid_token",
            "error_description": "Access token expired"
        }, status_code=401)
    
    # Return user info
    return JSONResponse({
        "sub": token_data['user_id'],
        "name": "Demo User",
        "email": "demo@example.com",
        "scope": token_data['scope']
    })

@app.route("/oauth/revoke", methods=["POST"])
async def oauth_revoke(request: Request):
    """OAuth 2.0 Token Revocation Endpoint."""
    try:
        form_data = await request.form()
        token = form_data.get('token')
        client_id = form_data.get('client_id')
        client_secret = form_data.get('client_secret')
        
        # Validate client credentials
        if client_id != OAUTH_CLIENT_ID or client_secret != OAUTH_CLIENT_SECRET:
            return JSONResponse({
                "error": "invalid_client",
                "error_description": "Invalid client credentials"
            }, status_code=401)
        
        # Revoke token (could be access or refresh token)
        if token in access_tokens:
            del access_tokens[token]
        elif token in refresh_tokens:
            # Also revoke associated access token
            refresh_data = refresh_tokens[token]
            if refresh_data['access_token'] in access_tokens:
                del access_tokens[refresh_data['access_token']]
            del refresh_tokens[token]
        
        return JSONResponse({})
        
    except Exception as e:
        return JSONResponse({
            "error": "server_error",
            "error_description": f"Internal server error: {str(e)}"
        }, status_code=500)

@app.route("/oauth/introspect", methods=["POST"])
async def oauth_introspect(request: Request):
    """OAuth 2.0 Token Introspection Endpoint."""
    try:
        form_data = await request.form()
        token = form_data.get('token')
        client_id = form_data.get('client_id')
        client_secret = form_data.get('client_secret')
        
        # Validate client credentials
        if client_id != OAUTH_CLIENT_ID or client_secret != OAUTH_CLIENT_SECRET:
            return JSONResponse({
                "error": "invalid_client",
                "error_description": "Invalid client credentials"
            }, status_code=401)
        
        # Check if token exists and is valid
        if token in access_tokens:
            token_data = access_tokens[token]
            is_active = time.time() <= token_data['expires_at']
            
            return JSONResponse({
                "active": is_active,
                "client_id": token_data['client_id'],
                "scope": token_data['scope'],
                "sub": token_data['user_id'],
                "exp": int(token_data['expires_at'])
            })
        else:
            return JSONResponse({"active": False})
            
    except Exception as e:
        return JSONResponse({
            "error": "server_error",
            "error_description": f"Internal server error: {str(e)}"
        }, status_code=500)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run enhanced MCP weather server")
    parser.add_argument("--port", type=int, default=int(os.getenv("MCP_SERVER_PORT", 8124)), help="Port to listen on")
    parser.add_argument("--host", type=str, default=os.getenv("MCP_SERVER_HOST", "localhost"), help="Host to bind to")
    parser.add_argument("--domain", type=str, help="Domain name to use for server URLs (e.g., example.com)")
    parser.add_argument("--api-key", type=str, help="OpenWeatherMap API key")
    args = parser.parse_args()
    
    if args.api_key:
        API_KEY = args.api_key
    
    # Use domain if provided, otherwise use host
    server_url = args.domain if args.domain else f"{args.host}:{args.port}"
    protocol = "https" if args.domain else "http"
    
    print(f"🌤️  Starting enhanced MCP weather server on {args.host}:{args.port}")
    print("📡 Available tools:")
    print("   - get_current_time: Get current timestamp")
    print("   - echo_message: Echo back a message")
    print("   - add_numbers: Add two numbers")
    print("   - get_weather: Get current weather for a city")
    print("   - get_forecast: Get weather forecast for a city")
    print("   - get_weather_alerts: Get weather alerts for a city")
    print("   - compare_cities_weather: Compare weather between two cities")
    print("   - get_server_info: Get server information")
    print("   - health_check: Server health status")
    print(f"🔑 API Status: {'***' + API_KEY[-4:] if len(API_KEY) > 4 else 'demo mode'}")
    print(f"🏥 Health endpoint: {protocol}://{server_url}/health")
    print(f"🔗 MCP endpoint: {protocol}://{server_url}/mcp")
    print("🔐 OAuth 2.0 endpoints:")
    print(f"   - Discovery: {protocol}://{server_url}/.well-known/oauth-authorization-server")
    print(f"   - Authorize: {protocol}://{server_url}/oauth/authorize")
    print(f"   - Token: {protocol}://{server_url}/oauth/token")
    print(f"   - UserInfo: {protocol}://{server_url}/oauth/userinfo")
    print(f"   - Revoke: {protocol}://{server_url}/oauth/revoke")
    print(f"   - Introspect: {protocol}://{server_url}/oauth/introspect")
    print(f"🆔 OAuth Client ID: {OAUTH_CLIENT_ID}")
    
    uvicorn.run(app, host=args.host, port=args.port)