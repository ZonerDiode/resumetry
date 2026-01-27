# Docker Setup for Resumetry

This project is containerized using Docker and Docker Compose.

## Prerequisites

- Docker Desktop (or Docker Engine + Docker Compose)

## Quick Start

### Build and Run with Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

Resumetry frontend will be available at: http://localhost:4200
Swagger for the FastAPI is available at: http://localhost:8000/api/docs
DynamoDB admin page is available at:http://localhost:8002

### Build Individual Images

```bash
# Build frontend image
cd frontend
docker build -t resumetry-frontend .

# Run frontend container
docker run -p 4200:80 resumetry-frontend
```

## Development

For development, you may want to run the Angular dev server directly:

```bash
cd frontend
npm install
npm start
```

This will start the dev server at http://localhost:4200 (default Angular port).

## Production Deployment

The Dockerfile uses a multi-stage build:
1. **Builder stage**: Installs dependencies and builds the Angular application
2. **Production stage**: Serves the built application using nginx

This results in a smaller, optimized production image.
