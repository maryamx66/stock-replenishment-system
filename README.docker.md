# Docker Deployment - Quick Reference

## Quick Start

1. **Create environment file:**

   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

2. **Start services:**

   ```bash
   ./start-docker.sh
   ```

   Or manually:

   ```bash
   docker compose up --build -d
   ```

3. **Access the application:**
   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Files Created

### Docker Configuration

- `backend/Dockerfile` - Backend Python container configuration
- `frontend/Dockerfile` - Frontend React/Vite container (multi-stage build)
- `docker-compose.yml` - Orchestrates both services
- `.dockerignore` - Root directory ignore patterns
- `frontend/.dockerignore` - Frontend specific ignore patterns
- `frontend/nginx.conf` - Nginx web server configuration

### Helper Scripts

- `start-docker.sh` - Convenience script for common Docker operations
- `DOCKER_DEPLOYMENT.md` - Comprehensive deployment guide

### Modified Files

- `backend/main.py` - Updated data paths for Docker environment
- `frontend/src/constants.js` - Added environment variable support for API base URL

## Architecture

```
┌─────────────────────────────────────────────┐
│          Reverse Proxy (Your Server)        │
│              (Port 80/443)                  │
└──────────────┬──────────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
┌─────────────┐  ┌──────────────┐
│  Frontend   │  │   Backend    │
│   (nginx)   │  │   (uvicorn)  │
│   Port 80   │  │  Port 8000   │
│             │  │              │
│  - React    │  │  - FastAPI   │
│  - Vite     │  │  - AI Engine │
│  - SPA      │  │  - Pandas    │
└─────────────┘  └──────┬───────┘
                        │
                        ▼
                ┌───────────────┐
                │  Grocery Data │
                │  (CSV Files)  │
                └───────────────┘
```

## Container Details

### Backend Container

- **Base Image:** python:3.11-slim
- **Size:** ~2GB (due to AI/ML dependencies)
- **Port:** 8000
- **Environment Variables:**
  - `GROQ_API_KEY`
  - `OPENROUTER_API_KEY`
  - `USE_GROQ`
- **Health Check:** Checks `/docs` endpoint every 30s
- **Data Volume:** `./grocery-data` mounted read-only

### Frontend Container

- **Build Stage:** node:20-alpine
- **Runtime Stage:** nginx:alpine
- **Size:** ~50MB
- **Port:** 80
- **Build Arg:** `VITE_API_BASE` (default: http://localhost:8000)
- **Health Check:** Checks root path every 30s

## Common Commands

```bash
# Start services
./start-docker.sh up

# View logs
./start-docker.sh logs

# Check status
./start-docker.sh status

# Restart services
./start-docker.sh restart

# Stop and remove
./start-docker.sh down

# Rebuild images
./start-docker.sh build
```

## Environment Variables

### Required (Backend)

- `GROQ_API_KEY` - Groq API key for AI services
- `OPENROUTER_API_KEY` - OpenRouter API key for AI services
- `USE_GROQ` - Set to 1 to use Groq, 0 for OpenRouter

### Optional

- `VITE_API_BASE` - Frontend API base URL (default: http://localhost:8000)

## Production Deployment

For production deployment with a custom domain:

1. **Update .env file:**

   ```env
   VITE_API_BASE=https://api.yourdomain.com
   ```

2. **Configure your reverse proxy** to route:
   - Frontend traffic → localhost:80
   - API traffic (`/api/*`) → localhost:8000

3. **Build and deploy:**
   ```bash
   docker compose build
   docker compose up -d
   ```

## Security Notes

- ✅ CORS configured for all origins (restrict in production)
- ✅ Grocery data mounted read-only
- ✅ Health checks enabled
- ✅ Environment variables externalized
- ⚠️ Update CORS origins in `backend/main.py` for production
- ⚠️ Use HTTPS via reverse proxy
- ⚠️ Keep API keys secure in `.env`

## Troubleshooting

See `DOCKER_DEPLOYMENT.md` for detailed troubleshooting steps.

**Common Issues:**

1. **Port conflicts:** Change ports in `docker-compose.yml`
2. **Build failures:** Check Docker logs with `docker compose logs`
3. **API not accessible:** Verify backend is healthy with `docker compose ps`
4. **Frontend env variables not working:** Rebuild with `docker compose build frontend`

## Resources

- Full deployment guide: `DOCKER_DEPLOYMENT.md`
- Backend API docs: http://localhost:8000/docs
- Docker documentation: https://docs.docker.com/
