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
DynamoDB admin page is available at: http://localhost:8002

