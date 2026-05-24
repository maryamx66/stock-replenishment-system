# Docker Deployment Guide

This guide explains how to deploy the Stock Replenishment System using Docker and Docker Compose.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- A `.env` file with your API keys (see below)

## Environment Setup

1. Copy the `.env.example` file to `.env`:

```bash
cp .env.example .env
```

2. Edit `.env` and add your API keys:

```env
GROQ_API_KEY=your_actual_groq_api_key
OPENROUTER_API_KEY=your_actual_openrouter_api_key
USE_GROQ=0  # Set to 1 to use Groq instead of OpenRouter
```

3. (Optional) Configure the API base URL for the frontend:

```env
VITE_API_BASE=http://your-backend-domain:8000
```

## Building and Running

### Quick Start (Development)

Build and start all services:

```bash
docker-compose up --build
```

This will:

- Build the backend service on port 8000
- Build the frontend service on port 80
- Start both services with automatic restart

### Production Deployment

1. **Build the images:**

```bash
docker-compose build
```

2. **Start the services in detached mode:**

```bash
docker-compose up -d
```

3. **Check service status:**

```bash
docker-compose ps
```

4. **View logs:**

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Service Configuration

### Backend Service

- **Port:** 8000
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/docs
- **Environment Variables:** Read from `.env` file

### Frontend Service

- **Port:** 80
- **URL:** http://localhost
- **API Base URL:** Configured via `VITE_API_BASE` (defaults to http://localhost:8000)

## Reverse Proxy Setup

Since you're using a reverse proxy on your server, you can configure it to route traffic:

### Example Nginx Configuration

```nginx
# Backend API
location /api/ {
    proxy_pass http://localhost:8000/api/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

# Frontend
location / {
    proxy_pass http://localhost:80/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### For Production with Custom Domain

Update your `.env` file before building:

```env
VITE_API_BASE=https://api.yourdomain.com
```

Then rebuild the frontend:

```bash
docker-compose build frontend
docker-compose up -d frontend
```

## Managing the Deployment

### Stop Services

```bash
docker-compose stop
```

### Start Existing Services

```bash
docker-compose start
```

### Restart Services

```bash
docker-compose restart
```

### Remove Services and Volumes

```bash
docker-compose down
```

### Update and Redeploy

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose up --build -d
```

## Troubleshooting

### Backend Issues

**Check backend logs:**

```bash
docker-compose logs backend
```

**Access backend container:**

```bash
docker exec -it stock-backend /bin/bash
```

**Verify data files:**

```bash
docker exec -it stock-backend ls -la grocery-data/
```

### Frontend Issues

**Check frontend logs:**

```bash
docker-compose logs frontend
```

**Access frontend container:**

```bash
docker exec -it stock-frontend /bin/sh
```

**Verify build output:**

```bash
docker exec -it stock-frontend ls -la /usr/share/nginx/html/
```

### Network Issues

**Check if services can communicate:**

```bash
docker-compose exec frontend wget -O- http://backend:8000/docs
```

### Port Conflicts

If ports 80 or 8000 are already in use, modify `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "8001:8000" # Use port 8001 instead

  frontend:
    ports:
      - "8080:80" # Use port 8080 instead
```

## Health Checks

Both services include health checks:

- **Backend:** Checks `/docs` endpoint every 30s
- **Frontend:** Checks root path every 30s

View health status:

```bash
docker-compose ps
```

## Security Recommendations

1. **Never commit the `.env` file** - It contains sensitive API keys
2. **Use strong API keys** - Generate secure keys for production
3. **Run behind a reverse proxy** - Use your server's reverse proxy with SSL/TLS
4. **Limit CORS origins** - Update `backend/main.py` to restrict allowed origins:
   ```python
   allow_origins=["https://yourdomain.com"]
   ```
5. **Keep Docker updated** - Regularly update Docker and images
6. **Monitor logs** - Set up log monitoring for production

## Resource Requirements

### Minimum Recommended

- **CPU:** 2 cores
- **RAM:** 4 GB
- **Disk:** 10 GB

### Backend

- **RAM:** ~2-3 GB (due to AI/ML dependencies)
- **CPU:** 1-2 cores

### Frontend

- **RAM:** ~100 MB
- **CPU:** Minimal

## Backup

Important directories to backup:

- `./grocery-data/` - Catalog and sales data
- `.env` - Environment configuration
- `backend/company_policy.txt` - Company policy document

## Support

For issues related to:

- **Docker:** Check Docker logs and documentation
- **Backend API:** Check `/docs` endpoint
- **Frontend:** Check browser console and network requests
