# MCP Weather Server Deployment Guide

## Quick Start (Local Testing)

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run locally:**
```bash
python I12_newMcpStreamable.py --host 0.0.0.0 --port 8124
```

## Server Deployment Options

### Option 1: Docker Deployment (Recommended)

1. **Clone/copy files to your server:**
```bash
# Copy these files to your server:
# - I12_newMcpStreamable.py
# - requirements.txt
# - Dockerfile
# - docker-compose.yml
# - .env.example
# - deploy.sh
```

2. **Set up environment:**
```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenWeatherMap API key
nano .env
```

3. **Deploy using script:**
```bash
./deploy.sh
```

### Option 2: Direct Server Installation

1. **Install Python 3.11+ on your server**

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set environment variables:**
```bash
export OPENWEATHER_API_KEY="your_api_key_here"
export MCP_SERVER_HOST="0.0.0.0"
export MCP_SERVER_PORT="8124"
```

4. **Run with systemd (production):**

Create `/etc/systemd/system/mcp-weather.service`:
```ini
[Unit]
Description=MCP Weather Server
After=network.target

[Service]
Type=simple
User=mcpuser
WorkingDirectory=/opt/mcp-weather
Environment=OPENWEATHER_API_KEY=your_api_key_here
Environment=MCP_SERVER_HOST=0.0.0.0
Environment=MCP_SERVER_PORT=8124
ExecStart=/usr/bin/python3 I12_newMcpStreamable.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable mcp-weather
sudo systemctl start mcp-weather
sudo systemctl status mcp-weather
```

### Option 3: Cloud Platform Deployment

#### Heroku
```bash
# Create Procfile
echo "web: python I12_newMcpStreamable.py --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy
heroku create your-mcp-server
heroku config:set OPENWEATHER_API_KEY=your_api_key
git push heroku main
```

#### DigitalOcean App Platform
```yaml
# app.yaml
name: mcp-weather-server
services:
- name: web
  source_dir: /
  github:
    repo: your-username/your-repo
    branch: main
  run_command: python I12_newMcpStreamable.py --host 0.0.0.0 --port $PORT
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: OPENWEATHER_API_KEY
    value: your_api_key_here
```

#### Railway
```json
{
  "build": {
    "commands": ["pip install -r requirements.txt"]
  },
  "deploy": {
    "startCommand": "python I12_newMcpStreamable.py --host 0.0.0.0 --port $PORT"
  }
}
```

## Configuration

### Environment Variables
- `OPENWEATHER_API_KEY`: Your OpenWeatherMap API key (get from https://openweathermap.org/api)
- `MCP_SERVER_HOST`: Host to bind to (default: localhost, use 0.0.0.0 for public access)
- `MCP_SERVER_PORT`: Port to listen on (default: 8124)

### Firewall Configuration
Open port 8124 (or your chosen port):
```bash
# UFW (Ubuntu)
sudo ufw allow 8124

# iptables
sudo iptables -A INPUT -p tcp --dport 8124 -j ACCEPT
```

## Health Monitoring

### Health Check Endpoint
- URL: `http://your-server:8124/health`
- Returns: JSON with server status and timestamp

### Monitoring Tools
```bash
# Check if server is responding
curl http://your-server:8124/health

# Monitor logs (Docker)
docker-compose logs -f

# Monitor logs (systemd)
sudo journalctl -u mcp-weather -f
```

## Security Considerations

1. **Use HTTPS in production** (add reverse proxy like nginx)
2. **Restrict access** with firewall rules if needed
3. **Keep API keys secure** (use environment variables)
4. **Regular updates** of dependencies
5. **Monitor logs** for unusual activity

## Accessing Your MCP Server

Once deployed, your server will be available at:
- Local: `http://localhost:8124`
- Server: `http://your-server-ip:8124`
- Cloud: `https://your-app-name.platform.com`

### MCP Tools Available:
- `get_weather(city)` - Current weather
- `get_forecast(city, days)` - Weather forecast
- `get_weather_alerts(city)` - Weather alerts
- `compare_cities_weather(city1, city2)` - Compare cities
- `get_current_time()` - Current timestamp
- `echo_message(message)` - Echo test
- `add_numbers(a, b)` - Math test
- `get_server_info()` - Server information
- `health_check()` - Health status

## Troubleshooting

### Common Issues:
1. **Port already in use**: Change port with `--port` flag
2. **API key issues**: Verify OpenWeatherMap API key is valid
3. **Network access**: Ensure firewall allows connections
4. **Docker issues**: Check Docker logs with `docker-compose logs`

### Debug Mode:
```bash
# Run with verbose logging
python I12_newMcpStreamable.py --host 0.0.0.0 --port 8124 --log-level debug
```