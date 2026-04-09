---
name: docker-expert
description: Docker containerization expert - multi-stage builds, image optimization, security hardening, Compose orchestration, and production deployment. Use for Dockerfile issues, image size, security, networking, and container orchestration.
---

# Docker Expert

Advanced Docker containerization expertise: optimization, security, multi-stage builds, orchestration, and production patterns.

## Workflow

1. **Scope check**: If the issue is outside Docker scope, redirect (see Handoff table below).
2. **Analyze**: Detect container setup using file tools first; shell commands as fallback.

   ```bash
   # Quick detection
   find . -name "Dockerfile*" -o -name "*compose*.yml" | head -10
   docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}" 2>/dev/null
   docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" 2>/dev/null
   ```

   Adapt to: existing Dockerfile patterns, multi-stage conventions, dev vs prod environment.

3. **Categorize**: Identify the problem area (see Core Expertise Areas or Issue Diagnostics).
4. **Apply**: Use the appropriate pattern from this skill.
5. **Validate**:

   ```bash
   docker build --no-cache -t test-build . && echo "Build OK"
   docker scout quickview test-build 2>/dev/null || echo "No Scout"
   docker-compose config && echo "Compose config valid"
   ```

## Core Expertise Areas

### 1. Dockerfile Optimization & Multi-Stage Builds

- **Layer caching**: Separate dependency install from source copy
- **Multi-stage builds**: Minimize production image size
- **Build context**: Comprehensive .dockerignore
- **Base image**: Alpine vs distroless vs scratch strategies

```dockerfile
# Optimized multi-stage pattern
FROM node:18-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build && npm prune --production

FROM node:18-alpine AS runtime
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001
WORKDIR /app
COPY --from=deps --chown=nextjs:nodejs /app/node_modules ./node_modules
COPY --from=build --chown=nextjs:nodejs /app/dist ./dist
COPY --from=build --chown=nextjs:nodejs /app/package*.json ./
USER nextjs
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1
CMD ["node", "dist/index.js"]
```

### 2. Container Security Hardening

- **Non-root user**: Proper user creation with specific UID/GID
- **Secrets management**: Docker secrets, build-time secrets (not ENV vars)
- **Base image security**: Regular updates, minimal attack surface
- **Runtime security**: Capability restrictions, resource limits

```dockerfile
# Security-hardened container
FROM node:18-alpine
RUN addgroup -g 1001 -S appgroup && \
    adduser -S appuser -u 1001 -G appgroup
WORKDIR /app
COPY --chown=appuser:appgroup package*.json ./
RUN npm ci --only=production
COPY --chown=appuser:appgroup . .
USER 1001
# Drop capabilities, set read-only root filesystem
```

### 3. Docker Compose Orchestration

- **Service dependencies**: Health checks, startup ordering
- **Networks**: Custom networks, service discovery, backend isolation
- **Environments**: Dev/staging/prod configurations separated
- **Volumes**: Named volumes, bind mounts, data persistence

```yaml
version: "3.8"
services:
  app:
    build:
      context: .
      target: production
    depends_on:
      db:
        condition: service_healthy
    networks:
      - frontend
      - backend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: 512M
        reservations:
          cpus: "0.25"
          memory: 256M

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB_FILE: /run/secrets/db_name
      POSTGRES_USER_FILE: /run/secrets/db_user
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_name
      - db_user
      - db_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true

volumes:
  postgres_data:

secrets:
  db_name:
    external: true
  db_user:
    external: true
  db_password:
    external: true
```

### 4. Image Size Optimization

**Size reduction strategies:**

- **Distroless images**: Minimal runtime environments
- **Build artifact optimization**: Remove build tools and cache
- **Layer consolidation**: Combine RUN commands strategically
- **Multi-stage artifact copying**: Only copy necessary files

```dockerfile
# Minimal production image
FROM gcr.io/distroless/nodejs18-debian11
COPY --from=build /app/dist /app
COPY --from=build /app/node_modules /app/node_modules
WORKDIR /app
EXPOSE 3000
CMD ["index.js"]
```

### 5. Development Workflow Integration

- **Hot reloading**: Volume mounting and file watching
- **Debugging**: Port exposure and debugging tools
- **Testing**: Test-specific containers and environments

```yaml
# Development override
services:
  app:
    build:
      context: .
      target: development
    volumes:
      - .:/app
      - /app/node_modules
      - /app/dist
    environment:
      - NODE_ENV=development
      - DEBUG=app:*
    ports:
      - "9229:9229" # Debug port
    command: npm run dev
```

### 6. Performance & Resource Management

- **Resource limits**: CPU/memory constraints for stability
- **Build performance**: Parallel builds, cache utilization
- **Runtime**: Process management, signal handling, metrics

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 1G
        reservations:
          cpus: "0.5"
          memory: 512M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
        window: 120s
```

## Advanced Problem-Solving Patterns

### Cross-Platform Builds

```bash
# Multi-architecture builds
docker buildx create --name multiarch-builder --use
docker buildx build --platform linux/amd64,linux/arm64 \
  -t myapp:latest --push .
```

### Build Cache Optimization

```dockerfile
# Mount build cache for package managers
FROM node:18-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci --only=production
```

### Secrets Management

```dockerfile
# Build-time secrets (BuildKit)
FROM alpine
RUN --mount=type=secret,id=api_key \
    API_KEY=$(cat /run/secrets/api_key) && \
    # Use API_KEY for build process
```

### Health Check Strategies

```dockerfile
# Sophisticated health monitoring
COPY health-check.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/health-check.sh
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD ["/usr/local/bin/health-check.sh"]
```

## Code Review Checklist

When reviewing Docker configurations, focus on:

### Dockerfile Optimization & Multi-Stage Builds

- [ ] Dependencies copied before source code for optimal layer caching
- [ ] Multi-stage builds separate build and runtime environments
- [ ] Production stage only includes necessary artifacts
- [ ] Build context optimized with comprehensive .dockerignore
- [ ] Base image selection appropriate (Alpine vs distroless vs scratch)
- [ ] RUN commands consolidated to minimize layers where beneficial

### Container Security Hardening

- [ ] Non-root user created with specific UID/GID (not default)
- [ ] Container runs as non-root user (USER directive)
- [ ] Secrets managed properly (not in ENV vars or layers)
- [ ] Base images kept up-to-date and scanned for vulnerabilities
- [ ] Minimal attack surface (only necessary packages installed)
- [ ] Health checks implemented for container monitoring

### Docker Compose & Orchestration

- [ ] Service dependencies properly defined with health checks
- [ ] Custom networks configured for service isolation
- [ ] Environment-specific configurations separated (dev/prod)
- [ ] Volume strategies appropriate for data persistence needs
- [ ] Resource limits defined to prevent resource exhaustion
- [ ] Restart policies configured for production resilience

### Image Size & Performance

- [ ] Final image size optimized (avoid unnecessary files/tools)
- [ ] Build cache optimization implemented
- [ ] Multi-architecture builds considered if needed
- [ ] Artifact copying selective (only required files)
- [ ] Package manager cache cleaned in same RUN layer

### Development Workflow Integration

- [ ] Development targets separate from production
- [ ] Hot reloading configured properly with volume mounts
- [ ] Debug ports exposed when needed
- [ ] Environment variables properly configured for different stages
- [ ] Testing containers isolated from production builds

### Networking & Service Discovery

- [ ] Port exposure limited to necessary services
- [ ] Service naming follows conventions for discovery
- [ ] Network security implemented (internal networks for backend)
- [ ] Load balancing considerations addressed
- [ ] Health check endpoints implemented and tested

## Common Issue Diagnostics

| Symptom                              | Root Cause                                        | Solution                                         |
| ------------------------------------ | ------------------------------------------------- | ------------------------------------------------ |
| Slow builds (10+ min), frequent miss | Poor layer ordering, large build context          | Multi-stage, .dockerignore, dependency caching   |
| Security scan failures, root user    | Outdated images, hardcoded secrets, default user  | Non-root user, secrets management, image updates |
| Images over 1 GB, slow deploys       | Build tools in prod, unnecessary files            | Distroless/multi-stage, artifact selection       |
| Service DNS / communication failures | Missing networks, port conflicts, naming errors   | Custom networks, health checks, service naming   |
| Hot reload failures, slow iteration  | Volume mount issues, port config, env mismatch    | Dev-specific targets, volume strategy, debug cfg |

## Handoff

| Scope beyond Docker              | Use instead                                    |
| -------------------------------- | ---------------------------------------------- |
| Kubernetes pods, services, mesh  | kubernetes-expert (future)                     |
| GitHub Actions CI/CD             | `skills/workflow-development/`                 |
| AWS ECS/Fargate, cloud services  | devops-expert                                  |
| Database persistence strategies  | database-expert                                |
| Application-level code perf      | language-specific skills                       |
