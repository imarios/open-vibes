# Development Dockerfiles

Building Dockerfiles for development prioritizes **fast iteration** and **rapid development**, contrasting with production Dockerfiles that optimize for performance and security.

## 1. Choose an Appropriate Base Image

Start your Dockerfile with the `FROM` instruction, specifying a suitable base image for your microservice's tech stack.

**Examples:**
- Node.js applications: `node:18.17.1`
- Python applications: `python:3.11-slim`
- Go applications: `golang:1.21`

You can choose from many public images available on Docker Hub.

```dockerfile
FROM node:18.17.1
```

## 2. Set the Working Directory

Use the `WORKDIR` instruction to define the directory inside the image where your application code will reside (e.g., `/usr/src/app`). Other paths in the Dockerfile will be relative to this directory.

```dockerfile
WORKDIR /usr/src/app
```

## 3. Copy Essential Files Early

**Always copy `package.json` and `package-lock.json` early** in the Dockerfile (e.g., `COPY package*.json ./`). This allows Docker to cache the dependency installation layer, speeding up subsequent builds if these files don't change.

```dockerfile
# Copy package files for caching
COPY package*.json ./
```

**Why this matters:**
- Docker caches each layer
- If package.json hasn't changed, Docker reuses the cached dependency installation
- Significantly speeds up rebuilds during development

## 4. Manage Source Code for Live Reload (Development Specific)

**Do NOT copy the source code directly into the Dockerfile for development**. This is a key difference from production Dockerfiles.

**Why:**
- If code were baked into the image, it couldn't be changed later without rebuilding the image
- This would hinder live reload and fast iteration

**Instead:**
The source code will be shared into the container using **Docker volumes** in the Docker Compose file.

```dockerfile
# DO NOT do this in development Dockerfile:
# COPY ./src ./src  ❌

# Source code is mounted via volumes in docker-compose.yaml instead
```

## 5. Install Dependencies for Development

Unlike production Dockerfiles that use `RUN npm ci --omit=dev` to install only production dependencies during the build process, **development Dockerfiles should install all dependencies (including `devDependencies` like `nodemon`) at container startup**.

Use `npm install --prefer-offline` within your `CMD` instruction to leverage caching on the host operating system, making subsequent container startups much faster.

**Development pattern:**
```dockerfile
# Dependencies installed at container startup (in CMD)
# Not during build (no RUN npm install here)
```

**Why:**
- Allows package.json changes without rebuilding the image
- Uses npm cache from host for faster installs
- Includes devDependencies needed for development

## 6. Define the Command to Start the Microservice (Development Specific)

The `CMD` instruction specifies the command invoked when the container is instantiated.

For development, this command should typically:
1. Install dependencies at startup
2. **Invoke a script that enables live reload**, such as `npm run start:dev`

This script often uses `nodemon` (e.g., `nodemon --legacy-watch ./src/index.js`) to automatically restart the microservice when code changes are detected.

```dockerfile
CMD npm install --prefer-offline && npm run start:dev
```

**Example package.json script:**
```json
{
  "scripts": {
    "start:dev": "nodemon --legacy-watch ./src/index.js"
  }
}
```

## 7. Use a .dockerignore File

Create a `.dockerignore` file in your project root to **specify files and directories that Docker should exclude from the build process**.

**Example .dockerignore:**
```
node_modules/
.git/
.github/
npm-debug.log
.env
.vscode/
*.md
dist/
coverage/
```

**Benefits:**
- Prevents unnecessary files from being copied into the build context
- Significantly **speeds up Docker builds**, especially as your project grows
- Reduces image size
- Prevents sensitive files from being included

## 8. Separate Development and Production Dockerfiles

It is a good practice to maintain **separate Dockerfiles for development (`Dockerfile-dev`) and production (`Dockerfile-prod`)**.

**Why:**
- Optimizes each for their specific needs
- Development: fast iteration and live reload
- Production: performance, security, and minimal dependencies
- Keeping them side-by-side helps ensure they remain in sync

**File structure:**
```
project/
├── Dockerfile-dev       # For development
├── Dockerfile-prod      # For production
├── .dockerignore
└── docker-compose.yaml
```

## Complete Example: Development Dockerfile

**Dockerfile-dev for Node.js:**
```dockerfile
FROM node:18.17.1

WORKDIR /usr/src/app

# Copy package files for dependency caching
COPY package*.json ./

# DO NOT copy source code (mounted via volume instead)

# Install dependencies and start with live reload
CMD npm install --prefer-offline && npm run start:dev
```

**Dockerfile-dev for Python:**
```dockerfile
FROM python:3.11-slim

WORKDIR /usr/src/app

# Copy requirements for dependency caching
COPY requirements.txt ./

# DO NOT copy source code (mounted via volume instead)

# Install dependencies and start with live reload
CMD pip install -r requirements.txt && python -m flask run --reload
```

## Key Differences: Development vs Production

| Aspect | Development Dockerfile | Production Dockerfile |
|--------|----------------------|----------------------|
| **Source code** | Mounted via volumes | Copied into image |
| **Dependencies** | Installed at startup | Installed during build |
| **Dev dependencies** | Included | Excluded (--omit=dev) |
| **Live reload** | Enabled (nodemon, etc.) | Disabled |
| **Optimization** | Fast iteration | Minimal size, security |
| **Caching** | npm cache from host | Self-contained |

## Best Practices Summary

1. ✅ Choose appropriate base image
2. ✅ Set WORKDIR early
3. ✅ Copy package files early for caching
4. ✅ DO NOT copy source code (use volumes)
5. ✅ Install dependencies at container startup
6. ✅ Enable live reload in CMD
7. ✅ Use .dockerignore to speed up builds
8. ✅ Separate dev and production Dockerfiles
