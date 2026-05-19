# Deployment Guide for CRIPT

## Prerequisites

- Ubuntu 20.04 LTS or later
- Python 3.10+
- Tailscale VPN (for secure networking)
- Git

## Step 1: System Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3.10 python3.10-venv python3.10-dev build-essential

# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Authenticate with Tailscale
sudo tailscale up

# Check your Tailscale IP
ip addr show tailscale0
# Output example: inet 100.120.170.116/32
```

## Step 2: Clone and Setup CRIPT

```bash
# Clone repository
git clone https://github.com/alvarofdezr/cript.git
cd cript

# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install CRIPT (uv creates venv automatically)
uv sync

# Verify installation
uv run python -c "import cript; print(cript.__version__)"
```

## Step 3: Run the Server

### Option 1: Direct Execution

```bash
# In terminal 1: Start server
uv run python -m cript.network.server

# Output: CRIPT Server listening on 0.0.0.0:5000
```

### Option 2: Systemd Service (Recommended)

Create `/etc/systemd/system/cript-server.service`:

```ini
[Unit]
Description=CRIPT Relay Server
After=network.target
Requires=tailscaled.service

[Service]
Type=simple
User=cript
WorkingDirectory=/opt/cript
ExecStart=/opt/cript/.venv/bin/python -m cript.network.server
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Setup:
```bash
# Create user and directories
sudo useradd -r cript
sudo mkdir -p /opt/cript
sudo cp -r . /opt/cript
sudo chown -R cript:cript /opt/cript

# Install uv and sync dependencies
sudo -u cript bash -c 'curl -LsSf https://astral.sh/uv/install.sh | sh'
sudo -u cript bash -c 'cd /opt/cript && ~/.cargo/bin/uv sync'

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable cript-server
sudo systemctl start cript-server

# Check status
sudo systemctl status cript-server
journalctl -u cript-server -f
```

## Step 4: Test Connectivity

### From Local Machine

```bash
# Install Tailscale on your machine
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# Get server Tailscale IP
ssh your-ubuntu-server "ip addr show tailscale0"

# Test connection
python examples/03_network.py
```

### From Another Ubuntu Server

```bash
# Install and connect Tailscale
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# Test connection to server
ping 100.120.170.116  # Replace with actual server IP

# Clone and test
git clone https://github.com/alvarofdezr/cript.git
cd cript
python examples/01_basic.py
```

## Step 5: Monitoring

### Check Logs

```bash
# System service logs
journalctl -u cript-server -f

# Custom logging (add to your server code)
import logging
logging.basicConfig(
    filename='/var/log/cript-server.log',
    level=logging.INFO
)
```

### Monitor Connections

```bash
# Check listening ports
sudo netstat -tuln | grep 5000

# List active connections
ss -tuln | grep 5000

# Monitor in real-time
watch -n 1 'ss -tuln | grep 5000'
```

### Metrics Collection

```bash
# Monitor CPU and memory
top -c -u cript

# Monitor network traffic
iftop -i tailscale0

# Monitor disk usage
df -h
```

## Step 6: Security Hardening

### Firewall Configuration

```bash
# Enable UFW (Ubuntu Firewall)
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow custom port (if not using Tailscale only)
sudo ufw allow 5000/tcp

# Check rules
sudo ufw status
```

### SSL/TLS (Optional - if exposing to public internet)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com

# Configure NGINX reverse proxy (see below)
```

### NGINX Reverse Proxy (Optional)

Create `/etc/nginx/sites-available/cript`:

```nginx
upstream cript_server {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://cript_server;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable:
```bash
sudo ln -s /etc/nginx/sites-available/cript /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Step 7: Backup and Recovery

### Automated Backup

Create `/opt/cript/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/backups/cript"
mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/cript-$(date +%Y%m%d-%H%M%S).tar.gz /opt/cript
find $BACKUP_DIR -mtime +30 -delete  # Keep last 30 days
```

Add to crontab:
```bash
sudo crontab -e
# Add: 0 2 * * * /opt/cript/backup.sh
```

### Recovery

```bash
tar -xzf /backups/cript/cript-YYYYMMDD-HHMMSS.tar.gz
```

## Docker Deployment (Alternative)

### Build Image

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install CRIPT
COPY . /app
RUN pip install --no-cache-dir .

# Expose port
EXPOSE 5000

# Run server
CMD ["python", "-m", "cript.network.server"]
```

### Build and Run

```bash
# Build
docker build -t cript:latest .

# Run
docker run -d \
  --name cript-server \
  --net tailscale \
  -p 5000:5000 \
  --restart always \
  cript:latest
```

### Docker Compose

```yaml
version: '3.8'

services:
  cript-server:
    build: .
    container_name: cript-server
    ports:
      - "5000:5000"
    restart: always
    environment:
      - PYTHONUNBUFFERED=1
    volumes:
      - ./logs:/app/logs
```

Run:
```bash
docker-compose up -d
```

## Troubleshooting

### Server Won't Start

```bash
# Check if port is in use
lsof -i :5000

# Kill process on port
sudo fuser -k 5000/tcp

# Check Python version
python --version

# Test import
python -c "from cript.network.server import CriptServer; print('OK')"
```

### Connection Issues

```bash
# Check Tailscale
sudo tailscale status

# Check network
ping 100.120.170.116

# Check firewall
sudo ufw status

# Test with telnet
telnet 100.120.170.116 5000
```

### High CPU/Memory

```bash
# Monitor process
ps aux | grep cript

# Check for zombie processes
ps aux | grep Z

# Restart service
sudo systemctl restart cript-server
```

## Performance Tuning

### Increase File Descriptors

```bash
# Modify /etc/security/limits.conf
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# Apply
sudo sysctl -p
```

### TCP Tuning

```bash
# /etc/sysctl.conf
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535
```

## Monitoring and Alerting

### Health Check Endpoint (Future Enhancement)

```python
@app.route('/health')
def health():
    return {'status': 'OK', 'timestamp': datetime.now()}
```

Monitor with:
```bash
while true; do
    curl -s http://localhost:5000/health || echo "DOWN"
    sleep 60
done
```

---

**Document Version**: 1.0  
**Last Updated**: May 2026
