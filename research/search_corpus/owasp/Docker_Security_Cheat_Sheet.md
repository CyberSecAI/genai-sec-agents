---
license: CC-BY-SA-4.0
path: owasp-cheatsheets/cheatsheets/Docker_Security_Cheat_Sheet.md
processed_at: null
security_domains:
- authentication
- docker
- network_security
- secrets
sha256: 92e8a7e63beddd920097806bca6aaa7070e6b22af40ba484e2ae96bbc99f7908
source: owasp-cheatsheet-series
tags:
- authentication
- docker
- network_security
- owasp
- secrets
---

# Docker Security Cheat Sheet

## Introduction

This cheat sheet provides security guidance for Docker containers and images.

## Container Security

### Run as Non-Root User

Always run containers as non-root users when possible.

```dockerfile
# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser
USER appuser
```

### Use Minimal Base Images

Use minimal base images to reduce attack surface:

```dockerfile
FROM alpine:3.18
# or
FROM scratch
```

### Set Resource Limits

Prevent resource exhaustion attacks:

```dockerfile
# In Dockerfile
RUN ulimit -n 1024

# At runtime
docker run --memory=512m --cpus=0.5 myapp
```

## Image Security

### Scan for Vulnerabilities

Regularly scan images for known vulnerabilities:

```bash
docker scan myapp:latest
```

### Multi-Stage Builds

Use multi-stage builds to minimize final image size:

```dockerfile
FROM node:18 as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
USER node
CMD ["npm", "start"]
```

### Sign Images

Sign container images for integrity verification:

```bash
docker trust sign myapp:latest
```

## Network Security

### Use Custom Networks

Create custom networks instead of default bridge:

```bash
docker network create --driver bridge mynetwork
docker run --network=mynetwork myapp
```

### Limit Port Exposure

Only expose necessary ports:

```dockerfile
EXPOSE 8080
```

## Secrets Management

### Never Hardcode Secrets

Use Docker secrets or external secret management:

```bash
echo "mysecret" | docker secret create db_password -
```

### Use Build-Time Secrets

For build-time secrets, use BuildKit:

```dockerfile
# syntax=docker/dockerfile:1
FROM alpine
RUN --mount=type=secret,id=mysecret cat /run/secrets/mysecret
```

## Runtime Security

### Read-Only Filesystem

Make containers read-only when possible:

```bash
docker run --read-only --tmpfs /tmp myapp
```

### Drop Capabilities

Remove unnecessary Linux capabilities:

```bash
docker run --cap-drop ALL --cap-add NET_BIND_SERVICE myapp
```

### Use Security Profiles

Apply AppArmor or SELinux profiles:

```bash
docker run --security-opt apparmor=docker-default myapp
```

## Monitoring and Logging

### Enable Logging

Configure appropriate logging drivers:

```bash
docker run --log-driver json-file --log-opt max-size=10m myapp
```

### Monitor Container Activity

Use tools like Falco for runtime security monitoring.