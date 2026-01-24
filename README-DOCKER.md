# Docker Setup for ResumeTry

This project is containerized using Docker and Docker Compose.

## Prerequisites

- Docker Desktop (or Docker Engine + Docker Compose)
- At least 2GB of available disk space

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

The frontend will be available at: http://localhost:4200

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

## Adding a Backend

When you're ready to add a backend service:

1. Create a `backend/Dockerfile`
2. Uncomment the backend service in `docker-compose.yml`
3. Configure the backend service as needed

## Troubleshooting

- **Port already in use**: Change the port mapping in `docker-compose.yml` (e.g., `"8080:80"`)
- **Build fails**: Ensure you have enough disk space and memory allocated to Docker
- **Container won't start**: Check logs with `docker-compose logs frontend`

