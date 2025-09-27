#!/bin/bash
cd /opt/protecht

# Install Python dependencies
pip3 install -r requirements.txt

# Fix import issues by setting PYTHONPATH
export PYTHONPATH=/opt/protecht

# Create a simple launcher script that handles imports correctly
cat > run_api.py << 'EOF'
import sys
import os
sys.path.insert(0, '/opt/protecht')

# Import and run the API server
from src.api_server import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

# Start the API server
nohup python3 run_api.py > api.log 2>&1 &

# Install nginx
yum install -y nginx

# Configure nginx
cat > /etc/nginx/conf.d/protecht.conf << 'EOF'
server {
    listen 80;
    server_name _;
    
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location / {
        return 200 "proTecht API Server";
        add_header Content-Type text/plain;
    }
}
EOF

# Start nginx
systemctl start nginx
systemctl enable nginx

# Wait for services to start
sleep 15

# Test the API
curl -f http://localhost/api/health || echo "API not ready yet"
