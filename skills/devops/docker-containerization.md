# Docker Containerization Skills

## Project Reference
- Repository: [titanic-devops-assessment](https://github.com/marjorieechu/titanic-devops-assessment)

## Skills Demonstrated

### Docker
- Writing Dockerfiles for Python/Flask applications
- Multi-stage builds and image optimization
- Development vs production Dockerfile configurations

### Docker Compose
- Multi-container orchestration (Flask API + PostgreSQL)
- Environment variable configuration
- Health checks and service dependencies
- Volume management for data persistence
- Development and production compose configurations

### Troubleshooting
- Resolving Python package version conflicts (Flask/Werkzeug compatibility)
- Fixing Python import paths for containerized applications
- Debugging container startup issues using `docker logs`

## Key Files
- `docker/Dockerfile` - Production Dockerfile
- `docker/Dockerfile.dev` - Development Dockerfile with hot-reload
- `docker-compose.yml` - Base compose configuration
- `docker-compose.dev.yml` - Development compose with volume mounts
- `docker-compose.prod.yml` - Production compose configuration

## Commands Learned
```bash
# Build and run containers
docker-compose -f docker-compose.dev.yml up --build

# Run in detached mode
docker-compose -f docker-compose.dev.yml up -d

# View container logs
docker logs -f <container-name>

# Stop containers
docker-compose -f docker-compose.dev.yml down
```
