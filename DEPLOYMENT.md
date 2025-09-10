# 📦 MCP Business Tools Server - Deployment Guide

This guide covers deployment options for the MCP Business Tools Server across different platforms and environments.

## 🌟 Deployment Options

1. [Local Development](#local-development)
2. [Cloud Deployment](#cloud-deployment)
3. [Docker Container](#docker-container)
4. [Kubernetes](#kubernetes)
5. [Serverless](#serverless)

---

## 🏠 Local Development

### Quick Start

```bash
# Clone and setup
git clone https://github.com/yourusername/Hubspot-CRM-MCP.git
cd Hubspot-CRM-MCP

# Virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run server
python3 business_tools_mcp.py
```

### Using systemd (Linux)

Create `/etc/systemd/system/mcp-server.service`:

```ini
[Unit]
Description=MCP Business Tools Server
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/Hubspot-CRM-MCP
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python business_tools_mcp.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable mcp-server
sudo systemctl start mcp-server
sudo systemctl status mcp-server
```

---

## ☁️ Cloud Deployment

### AWS EC2

1. **Launch EC2 Instance**
```bash
# Amazon Linux 2 or Ubuntu 20.04
# Instance type: t3.small or larger
# Security group: Allow SSH (22) and your app port
```

2. **Setup on Instance**
```bash
# Connect to instance
ssh -i your-key.pem ec2-user@your-instance-ip

# Install Python
sudo yum install python3 python3-pip git -y  # Amazon Linux
# or
sudo apt update && sudo apt install python3 python3-pip git -y  # Ubuntu

# Clone repository
git clone https://github.com/yourusername/Hubspot-CRM-MCP.git
cd Hubspot-CRM-MCP

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
nano .env  # Add your API keys

# Install and configure supervisor
sudo pip install supervisor
sudo mkdir -p /etc/supervisor/conf.d

# Create supervisor config
sudo nano /etc/supervisor/conf.d/mcp-server.conf
```

Supervisor config:
```ini
[program:mcp-server]
command=/home/ec2-user/Hubspot-CRM-MCP/venv/bin/python business_tools_mcp.py
directory=/home/ec2-user/Hubspot-CRM-MCP
user=ec2-user
autostart=true
autorestart=true
stderr_logfile=/var/log/mcp-server.err.log
stdout_logfile=/var/log/mcp-server.out.log
```

### Google Cloud Platform

1. **Create Compute Engine Instance**
```bash
gcloud compute instances create mcp-server \
  --zone=us-central1-a \
  --machine-type=e2-small \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud
```

2. **Deploy Application**
```bash
# SSH into instance
gcloud compute ssh mcp-server

# Follow same setup as AWS EC2
```

### Azure VM

```bash
# Create resource group
az group create --name mcp-rg --location eastus

# Create VM
az vm create \
  --resource-group mcp-rg \
  --name mcp-server \
  --image UbuntuLTS \
  --admin-username azureuser \
  --generate-ssh-keys

# SSH and deploy
ssh azureuser@<public-ip>
# Follow same setup steps
```

### Heroku

1. **Create `Procfile`**:
```
worker: python business_tools_mcp.py
```

2. **Create `runtime.txt`**:
```
python-3.11.0
```

3. **Deploy**:
```bash
heroku create mcp-business-tools
heroku config:set $(cat .env | xargs)
git push heroku main
heroku ps:scale worker=1
```

---

## 🐳 Docker Container

### Dockerfile

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY business_tools_mcp.py .
COPY config.py .

# Create non-root user
RUN useradd -m -u 1000 mcp && chown -R mcp:mcp /app
USER mcp

# Run server
CMD ["python", "business_tools_mcp.py"]
```

### Build and Run

```bash
# Build image
docker build -t mcp-business-tools:latest .

# Run container
docker run -d \
  --name mcp-server \
  --restart always \
  --env-file .env \
  -v $(pwd)/credentials.json:/app/credentials.json:ro \
  -v $(pwd)/google_calendar_token.pickle:/app/google_calendar_token.pickle \
  mcp-business-tools:latest

# View logs
docker logs -f mcp-server
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  mcp-server:
    build: .
    container_name: mcp-server
    restart: always
    env_file:
      - .env
    volumes:
      - ./credentials.json:/app/credentials.json:ro
      - ./google_calendar_token.pickle:/app/google_calendar_token.pickle
      - ./logs:/app/logs
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

Run with:
```bash
docker-compose up -d
docker-compose logs -f
```

---

## ⚓ Kubernetes

### Deployment YAML

Create `k8s-deployment.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mcp-config
data:
  SERPAPI_KEY: "your_key"
  # Add other non-sensitive config

---
apiVersion: v1
kind: Secret
metadata:
  name: mcp-secrets
type: Opaque
data:
  HUBSPOT_TOKEN: <base64-encoded>
  TWILIO_AUTH_TOKEN: <base64-encoded>
  # Add other sensitive data

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-server
spec:
  replicas: 2
  selector:
    matchLabels:
      app: mcp-server
  template:
    metadata:
      labels:
        app: mcp-server
    spec:
      containers:
      - name: mcp-server
        image: mcp-business-tools:latest
        resources:
          limits:
            memory: "512Mi"
            cpu: "500m"
          requests:
            memory: "256Mi"
            cpu: "250m"
        envFrom:
        - configMapRef:
            name: mcp-config
        - secretRef:
            name: mcp-secrets
        volumeMounts:
        - name: credentials
          mountPath: /app/credentials.json
          subPath: credentials.json
      volumes:
      - name: credentials
        configMap:
          name: google-credentials
```

Deploy:
```bash
kubectl apply -f k8s-deployment.yaml
kubectl get pods
kubectl logs -f deployment/mcp-server
```

---

## 🚀 Serverless

### AWS Lambda

1. **Create deployment package**:
```bash
# Create lambda_function.py
cat > lambda_function.py << 'EOF'
import json
import asyncio
from business_tools_mcp import *

def lambda_handler(event, context):
    tool = event['tool']
    params = event['params']
    
    # Get the tool function
    tool_func = globals().get(f"{tool}_tool")
    if not tool_func:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': f'Tool {tool} not found'})
        }
    
    # Run async function
    result = asyncio.run(tool_func(params))
    
    return {
        'statusCode': 200,
        'body': json.dumps(result[0].text if result else {})
    }
EOF

# Package for Lambda
pip install -r requirements.txt -t lambda_package/
cp business_tools_mcp.py config.py lambda_function.py lambda_package/
cd lambda_package
zip -r ../lambda_deployment.zip .
```

2. **Deploy to Lambda**:
```bash
aws lambda create-function \
  --function-name mcp-business-tools \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR_ACCOUNT:role/lambda-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://lambda_deployment.zip \
  --timeout 60 \
  --memory-size 512
```

### Google Cloud Functions

```python
# main.py
import functions_framework
import asyncio
from business_tools_mcp import *

@functions_framework.http
def mcp_handler(request):
    request_json = request.get_json()
    tool = request_json['tool']
    params = request_json['params']
    
    tool_func = globals().get(f"{tool}_tool")
    if not tool_func:
        return {'error': f'Tool {tool} not found'}, 404
    
    result = asyncio.run(tool_func(params))
    return json.loads(result[0].text if result else '{}')
```

Deploy:
```bash
gcloud functions deploy mcp-business-tools \
  --runtime python311 \
  --trigger-http \
  --entry-point mcp_handler \
  --memory 512MB \
  --timeout 60s \
  --env-vars-file .env.yaml
```

---

## 📊 Monitoring & Logging

### CloudWatch (AWS)

```python
# Add to business_tools_mcp.py
import boto3
cloudwatch = boto3.client('cloudwatch')

def log_metric(tool_name, success):
    cloudwatch.put_metric_data(
        Namespace='MCP/Tools',
        MetricData=[
            {
                'MetricName': 'ToolExecution',
                'Dimensions': [
                    {'Name': 'Tool', 'Value': tool_name},
                    {'Name': 'Status', 'Value': 'Success' if success else 'Error'}
                ],
                'Value': 1,
                'Unit': 'Count'
            }
        ]
    )
```

### Datadog

```bash
# Install Datadog agent
DD_AGENT_MAJOR_VERSION=7 DD_API_KEY=your_api_key \
  DD_SITE="datadoghq.com" bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script.sh)"

# Add to your code
from datadog import initialize, statsd

initialize(statsd_host='localhost', statsd_port=8125)

# Log metrics
statsd.increment('mcp.tool.execution', tags=[f'tool:{tool_name}'])
```

---

## 🔒 Security Considerations

### Environment Variables

Never commit `.env` files. Use:
- AWS Secrets Manager
- Azure Key Vault
- Google Secret Manager
- HashiCorp Vault

### Network Security

```bash
# Firewall rules (iptables)
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT  # SSH
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT # HTTPS
sudo iptables -A INPUT -j DROP  # Drop all other

# Save rules
sudo iptables-save > /etc/iptables/rules.v4
```

### SSL/TLS with Nginx

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain/privkey.pem;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy MCP Server

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest
    
    - name: Run tests
      run: pytest tests/
    
    - name: Build Docker image
      run: docker build -t mcp-server:${{ github.sha }} .
    
    - name: Push to registry
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker push mcp-server:${{ github.sha }}
    
    - name: Deploy to server
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USERNAME }}
        key: ${{ secrets.SSH_KEY }}
        script: |
          docker pull mcp-server:${{ github.sha }}
          docker stop mcp-server || true
          docker run -d --name mcp-server --env-file .env mcp-server:${{ github.sha }}
```

---

## 📈 Scaling Strategies

### Horizontal Scaling

- Use Kubernetes HPA (Horizontal Pod Autoscaler)
- AWS Auto Scaling Groups
- Load balancer (Nginx, HAProxy, AWS ALB)

### Vertical Scaling

- Increase instance size
- Add more CPU/Memory
- Optimize code performance

### Caching

- Redis for API responses
- CloudFront for static assets
- In-memory caching for frequent queries

---

## 🆘 Troubleshooting

### Common Issues

1. **Port already in use**
```bash
lsof -i :8080
kill -9 <PID>
```

2. **Permission denied**
```bash
chmod +x business_tools_mcp.py
sudo chown -R $USER:$USER /path/to/project
```

3. **Module not found**
```bash
pip install --upgrade -r requirements.txt
python -m pip install --upgrade pip
```

4. **Memory issues**
```bash
# Check memory usage
free -h
top -o %MEM

# Increase swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 📚 Additional Resources

- [MCP Documentation](https://modelcontextprotocol.io)
- [Docker Documentation](https://docs.docker.com)
- [Kubernetes Documentation](https://kubernetes.io/docs)
- [AWS Documentation](https://docs.aws.amazon.com)

---

**Need help?** Open an issue on GitHub or check the troubleshooting section.
