# Deployment Guide

This guide provides detailed instructions for deploying the IoT Device Controller application in a production environment.

## Production Deployment Overview

For a production deployment, you'll need to consider the following components:

1. **Web Application Server**: Running the Flask application with a production WSGI server
2. **MQTT Broker**: A secure and scalable MQTT broker service
3. **Database**: A production-ready database system
4. **Reverse Proxy**: For SSL termination and serving static files
5. **Monitoring**: Keeping track of application health

## Prerequisites

- Linux server (Ubuntu 20.04+ recommended)
- Python 3.8+
- PostgreSQL 12+
- Nginx
- Domain name with SSL certificate
- Mosquitto MQTT Broker

## Step 1: Server Preparation

Update the server and install required packages:

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv postgresql nginx certbot python3-certbot-nginx git mosquitto mosquitto-clients
```

## Step 2: Database Setup

Create a PostgreSQL database and user:

```bash
sudo -u postgres psql

postgres=# CREATE DATABASE iot_controller;
postgres=# CREATE USER iot_user WITH PASSWORD 'secure_password';
postgres=# GRANT ALL PRIVILEGES ON DATABASE iot_controller TO iot_user;
postgres=# \q
```

## Step 3: Application Setup

1. Clone the repository:

```bash
git clone https://github.com/SNO7E-G/IoT-Device-Controller.git
cd IoT-Device-Controller
```

2. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

4. Create a `.env` file with production settings:

```
SECRET_KEY=your_secure_secret_key
DATABASE_URI=postgresql://iot_user:secure_password@localhost/iot_controller
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_USERNAME=mqtt_user
MQTT_PASSWORD=mqtt_password
```

5. Initialize the database:

```bash
flask db upgrade
```

## Step 4: MQTT Broker Configuration

1. Configure Mosquitto with authentication:

```bash
sudo nano /etc/mosquitto/mosquitto.conf
```

Add the following configuration:

```
listener 1883 localhost
listener 8883
certfile /etc/letsencrypt/live/yourdomain.com/cert.pem
keyfile /etc/letsencrypt/live/yourdomain.com/privkey.pem
allow_anonymous false
password_file /etc/mosquitto/passwd
```

2. Create a password file:

```bash
sudo mosquitto_passwd -c /etc/mosquitto/passwd mqtt_user
```

3. Restart Mosquitto:

```bash
sudo systemctl restart mosquitto
```

## Step 5: WSGI Configuration

1. Create a WSGI entry point file (`wsgi.py`):

```python
from app import app

if __name__ == "__main__":
    app.run()
```

2. Create a systemd service file:

```bash
sudo nano /etc/systemd/system/iot-controller.service
```

Add the following content:

```
[Unit]
Description=IoT Device Controller
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/IoT-Device-Controller
Environment="PATH=/path/to/IoT-Device-Controller/venv/bin"
ExecStart=/path/to/IoT-Device-Controller/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

3. Start and enable the service:

```bash
sudo systemctl start iot-controller
sudo systemctl enable iot-controller
```

## Step 6: Nginx Configuration

1. Obtain SSL certificates:

```bash
sudo certbot --nginx -d yourdomain.com
```

2. Create an Nginx configuration file:

```bash
sudo nano /etc/nginx/sites-available/iot-controller
```

Add the following content:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location /static {
        alias /path/to/IoT-Device-Controller/app/static;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /socket.io {
        proxy_pass http://127.0.0.1:8000/socket.io;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

3. Enable the site and restart Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/iot-controller /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Step 7: Monitoring Setup (Optional)

For production monitoring, consider setting up:

1. **Prometheus and Grafana** for metrics collection and visualization
2. **Loki** for log aggregation
3. **AlertManager** for alerts

You can install these tools using Docker:

```bash
sudo apt install -y docker.io docker-compose
git clone https://github.com/vegasbrianc/prometheus.git
cd prometheus
docker-compose up -d
```

## Backup Strategy

Set up regular backups of your database and configuration:

```bash
# Create a backup script
sudo nano /usr/local/bin/backup-iot.sh
```

Add the following content:

```bash
#!/bin/bash
DATE=$(date +%Y-%m-%d)
BACKUP_DIR="/path/to/backups"

# Database backup
pg_dump -U iot_user iot_controller > $BACKUP_DIR/db-$DATE.sql

# Application backup
tar -czf $BACKUP_DIR/app-$DATE.tar.gz /path/to/IoT-Device-Controller

# Keep only last 7 backups
find $BACKUP_DIR -name "db-*.sql" -type f -mtime +7 -delete
find $BACKUP_DIR -name "app-*.tar.gz" -type f -mtime +7 -delete
```

Make it executable and set up a cron job:

```bash
sudo chmod +x /usr/local/bin/backup-iot.sh
sudo crontab -e
```

Add a daily backup job:

```
0 2 * * * /usr/local/bin/backup-iot.sh
```

## Security Considerations

1. **Firewall Configuration**:

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8883/tcp  # MQTT over TLS
sudo ufw enable
```

2. **Regular Updates**:

```bash
# Create an update script
sudo nano /usr/local/bin/update-server.sh
```

Add:

```bash
#!/bin/bash
apt update
apt upgrade -y
```

3. **Application Secrets Management**:
   - Keep secrets in environment variables or a secure .env file
   - Never commit secrets to version control
   - Consider using a secrets management tool like HashiCorp Vault for larger deployments

## Load Balancing and Scaling (for High Traffic)

For high-traffic deployments, consider:

1. **Horizontal Scaling**:
   - Multiple application servers behind a load balancer
   - Use Nginx or HAProxy as a load balancer

2. **Database Scaling**:
   - PostgreSQL with read replicas
   - Connection pooling with PgBouncer

3. **MQTT Broker Scaling**:
   - MQTT broker cluster (e.g., EMQ X or HiveMQ)
   - MQTT load balancing

## Troubleshooting

Common issues and solutions:

1. **Application not starting**:
   - Check logs: `sudo journalctl -u iot-controller`
   - Verify environment variables: `cat /path/to/.env`
   - Ensure database connection: `psql -U iot_user -d iot_controller`

2. **MQTT connection issues**:
   - Test MQTT broker: `mosquitto_sub -h localhost -p 1883 -u mqtt_user -P mqtt_password -t "test/topic"`
   - Check Mosquitto logs: `sudo journalctl -u mosquitto`

3. **Nginx not working**:
   - Check configuration: `sudo nginx -t`
   - Verify SSL: `sudo certbot certificates`
   - Check logs: `sudo tail -f /var/log/nginx/error.log`

## Maintenance Procedures

1. **Application Updates**:

```bash
cd /path/to/IoT-Device-Controller
git pull
source venv/bin/activate
pip install -r requirements.txt
flask db upgrade
sudo systemctl restart iot-controller
```

2. **Database Maintenance**:

```bash
sudo -u postgres psql -d iot_controller -c "VACUUM ANALYZE;"
```

3. **Log Rotation**:

Ensure logs are properly rotated using logrotate:

```bash
sudo nano /etc/logrotate.d/iot-controller
```

Add:

```
/path/to/IoT-Device-Controller/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
}
```

---

© 2024 Mahmoud Ashraf (SNO7E). All rights reserved. 