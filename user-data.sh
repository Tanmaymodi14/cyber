#!/bin/bash
set -euxo pipefail
dnf update -y
dnf install -y python3.11 python3.11-devel git nginx
alternatives --set python3 /usr/bin/python3.11 || true

# App dir
mkdir -p /opt/protecht
cd /opt/protecht

# Pull artifact from S3
yum install -y unzip tar
aws s3 cp s3://'"$S3_BUCKET"'/protecht-app.tar.gz /opt/protecht/protecht-app.tar.gz --region '"$AWS_REGION"'
tar -xzf protecht-app.tar.gz

# Python venv + deps
python3 -m venv /opt/protecht/venv
source /opt/protecht/venv/bin/activate
pip install --upgrade pip
# Use the deploy reqs (fastapi, uvicorn, boto3, pydantic, multipart)
pip install -r /opt/protecht/proTecht/deploy_package/requirements.txt

# Systemd service for Uvicorn
cat >/etc/systemd/system/protecht.service <<'EOF'
[Unit]
Description=proTecht FastAPI service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/protecht/proTecht
Environment=PYTHONPATH=/opt/protecht/proTecht
Environment=ENABLE_AI=false
ExecStart=/opt/protecht/venv/bin/uvicorn src.api_server:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable protecht
systemctl start protecht

# Nginx reverse proxy :80 -> :8000
cat >/etc/nginx/conf.d/protecht.conf <<'EOF'
server {
    listen 80 default_server;
    server_name _;

    location / {
        proxy_pass         http://127.0.0.1:8000\;
        proxy_http_version 1.1;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
    }
}
EOF

nginx -t && systemctl enable nginx && systemctl restart nginx
