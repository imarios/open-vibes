# Docker Compose for Development

Docker Compose is a crucial tool for defining, building, running, and managing *multiple* containers for **local development and testing**, effectively simulating your microservices application on your development machine. It significantly simplifies the process compared to running individual Docker commands for each service.

## 1. File Naming and Location

- Name your Docker Compose file `docker-compose.yaml`
- Place it in the **root directory of your microservices application**, as it orchestrates multiple services and doesn't belong to any single one

```
my-microservices-app/
├── docker-compose.yaml      # At root
├── service-a/
├── service-b/
└── service-c/
```

## 2. Define Services with Versioning

Start with `version: '3'` to specify the Docker Compose file format. List each microservice or external service (like databases, message queues) under the `services:` field.

```yaml
version: '3'

services:
  web:
    # Service configuration
  database:
    # Service configuration
  cache:
    # Service configuration
```

## 3. Organize Microservices in Subdirectories

Adopt a convention where each microservice resides in its **own separate subdirectory**, typically named after the microservice.

```
my-app/
├── docker-compose.yaml
├── video-streaming/
│   ├── Dockerfile-dev
│   ├── package.json
│   └── src/
├── history/
│   ├── Dockerfile-dev
│   ├── package.json
│   └── src/
└── api-gateway/
    ├── Dockerfile-dev
    ├── package.json
    └── src/
```

## 4. Configure Image Building for Each Service

For each microservice that you build locally, specify the `build` context and the **development Dockerfile**.

```yaml
services:
  video-streaming:
    build:
      context: ./video-streaming
      dockerfile: Dockerfile-dev
    # Other configuration...
```

**Important:** When invoking `docker compose up`, always use the `--build` argument in development to ensure your latest code changes are included.

```bash
docker compose up --build
```

## 5. Assign Meaningful Container Names

Assign a clear `container_name` to each service (e.g., `video-streaming`, `history`, `db`, `rabbit`).

**Benefits:**
- Helps differentiate output when multiple services are logging simultaneously
- Allows services to refer to each other by name within the Docker network

```yaml
services:
  video-streaming:
    container_name: video-streaming
    build:
      context: ./video-streaming
      dockerfile: Dockerfile-dev
```

## 6. Map Ports for Host Access

Use the `ports:` mapping to expose container ports to your host machine.

Choose unique host ports for each service to avoid conflicts (e.g., 4000, 4001, 4002...). This allows you to access services from your web browser or other local tools.

```yaml
services:
  video-streaming:
    container_name: video-streaming
    ports:
      - "4000:80"    # Host:Container

  history:
    container_name: history
    ports:
      - "4001:80"

  api-gateway:
    container_name: api-gateway
    ports:
      - "4002:80"
```

## 7. Configure with Environment Variables

Pass **environment variables** to your containers to configure microservices.

### Static Environment Variables

```yaml
services:
  web:
    environment:
      - PORT=80
      - NODE_ENV=development
      - DBHOST=db
      - DBNAME=myapp
```

### Dynamic/Sensitive Values from Host

For sensitive or dynamic values (like cloud storage credentials), refer to **host environment variables** using `${VAR_NAME}`. These values must be set in your terminal before starting Docker Compose.

```yaml
services:
  web:
    environment:
      - STORAGE_ACCOUNT_NAME=${STORAGE_ACCOUNT_NAME}
      - STORAGE_ACCOUNT_KEY=${STORAGE_ACCOUNT_KEY}
      - VIDEO_STORAGE_HOST=${VIDEO_STORAGE_HOST}
```

**Set in terminal before running:**
```bash
export STORAGE_ACCOUNT_NAME=myaccount
export STORAGE_ACCOUNT_KEY=mykey
docker compose up
```

### Development-Specific Logic

Set `NODE_ENV=development` to activate development-specific logic within your microservices.

## 8. Enable Live Reload with Docker Volumes

This is a **critical step for efficient development**.

### Mount Source Code Directory

**Mount your microservice's source code directory** from the host to the container. This allows changes made on your development computer to automatically propagate to the running container, triggering `nodemon` to restart the service.

```yaml
services:
  history:
    volumes:
      - ./history/src:/usr/src/app/src:z
```

### Mount npm Cache Volume

**Mount a volume for the `npm` cache**. This caches downloaded npm packages on the host, significantly speeding up `npm install` during subsequent container startups or rebuilds.

```yaml
services:
  history:
    volumes:
      - ./history/src:/usr/src/app/src:z
      - /tmp/history/npm-cache:/root/.npm:z
```

**The `:z` flag** indicates the volume is shared and correctly handled by Docker (SELinux compatibility).

### Complete Example

```yaml
services:
  video-streaming:
    container_name: video-streaming
    build:
      context: ./video-streaming
      dockerfile: Dockerfile-dev
    ports:
      - "4000:80"
    volumes:
      # Source code for live reload
      - ./video-streaming/src:/usr/src/app/src:z
      # npm cache for faster installs
      - /tmp/video-streaming/npm-cache:/root/.npm:z
    environment:
      - PORT=80
      - NODE_ENV=development
```

## 9. Manage Service Dependencies

Use `depends_on:` to specify the order in which services should start. This ensures your application components come online in a predictable and functional sequence.

```yaml
services:
  web:
    depends_on:
      - db
      - rabbit

  db:
    image: postgres:15

  rabbit:
    image: rabbitmq:3.12-management
```

**Note:** `depends_on` only controls startup order, not readiness. The dependent service may start before the dependency is fully ready. For production, consider health checks.

## 10. Define Restart Policy

For development, it's often useful to set `restart: "no"`. This prevents Docker Compose from automatically restarting a crashed container, allowing you to inspect its state and debug manually.

```yaml
services:
  web:
    restart: "no"
```

**Options:**
- `"no"` - Never restart (good for development debugging)
- `always` - Always restart
- `on-failure` - Restart only on failure
- `unless-stopped` - Restart unless manually stopped

## 11. Integrate External Services

Easily add services like **MongoDB**, **PostgreSQL**, and **RabbitMQ** by pulling public images from Docker Hub.

```yaml
services:
  # Your application services...

  db:
    image: postgres:15
    container_name: db
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=dev
      - POSTGRES_PASSWORD=devpass
      - POSTGRES_DB=myapp
    volumes:
      - postgres-data:/var/lib/postgresql/data

  rabbit:
    image: rabbitmq:3.12-management
    container_name: rabbit
    ports:
      - "5672:5672"    # AMQP
      - "15672:15672"  # Management UI
    environment:
      - RABBITMQ_DEFAULT_USER=dev
      - RABBITMQ_DEFAULT_PASS=devpass

  mongo:
    image: mongo:7.0
    container_name: mongo
    ports:
      - "27017:27017"
    environment:
      - MONGO_INITDB_ROOT_USERNAME=dev
      - MONGO_INITDB_ROOT_PASSWORD=devpass

volumes:
  postgres-data:
```

## 12. Consider Mock Services for External Dependencies

For development, replace real external services (like cloud storage) with **simpler "mock" versions** that use local resources.

**Benefits:**
- Reduces external dependencies
- Simplifies local setup
- Prevents developers from interfering with each other's cloud resources

**Ensure the mock service conforms to the same API interface as the real one.**

```yaml
services:
  # Instead of real Azure Storage
  mock-storage:
    build:
      context: ./mock-storage
    container_name: mock-storage
    ports:
      - "9000:9000"
    volumes:
      - ./mock-storage/data:/data
```

**Example:** Use local filesystem instead of Azure Storage, but expose the same REST API.

## 13. Database Fixtures for Testing

While not directly in the Docker Compose file, consider including a **dedicated "database fixtures REST API" container** in your Docker Compose setup for loading test data.

This allows your automated tests (e.g., Playwright end-to-end tests) to easily populate the database with known data before running tests.

```yaml
services:
  db-fixtures:
    build:
      context: ./db-fixtures
    container_name: db-fixtures
    depends_on:
      - db
    ports:
      - "9001:80"
```

## 14. Essential Docker Compose Commands for Development

### Start Everything (Most Important)

```bash
docker compose up --build
```

This is the **most important command**. It builds all specified images and starts all containers defined in your `docker-compose.yaml` file. Always use `--build` in development to ensure changes are picked up.

### List Running Containers

```bash
docker compose ps
```

Lists running containers that are part of your application.

### Stop Containers

```bash
docker compose stop
```

Stops all containers in the application, but keeps them for inspection.

### Destroy Everything

```bash
docker compose down --volumes
```

**Stops and destroys the application completely**, removing containers and associated volumes, leaving your development machine in a clean state. Use `--volumes` to ensure old filesystems are not restored on reboot.

### Clean Reboot

```bash
docker compose down --volumes && docker compose up --build
```

A chained command for a clean reboot of your entire application.

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f web

# Last 100 lines
docker compose logs --tail=100 -f
```

### Execute Commands in Running Container

```bash
docker compose exec web bash
docker compose exec db psql -U dev myapp
```

## 15. Use Shell Scripts for Convenience

Wrap frequently used Docker Compose commands in simple shell scripts to streamline your daily development workflow.

**up.sh:**
```bash
#!/bin/bash
docker compose up --build
```

**down.sh:**
```bash
#!/bin/bash
docker compose down --volumes
```

**reboot.sh:**
```bash
#!/bin/bash
docker compose down --volumes && docker compose up --build
```

**Make scripts executable:**
```bash
chmod +x up.sh down.sh reboot.sh
```

**Usage:**
```bash
./up.sh      # Start development environment
./down.sh    # Clean shutdown
./reboot.sh  # Clean restart
```

## Complete Example: Docker Compose for Development

```yaml
version: '3'

services:
  # Application Services
  web:
    container_name: web
    build:
      context: ./web
      dockerfile: Dockerfile-dev
    ports:
      - "4000:80"
    volumes:
      - ./web/src:/usr/src/app/src:z
      - /tmp/web/npm-cache:/root/.npm:z
    environment:
      - PORT=80
      - NODE_ENV=development
      - DATABASE_URL=postgresql://dev:devpass@db:5432/myapp
    depends_on:
      - db
    restart: "no"

  api:
    container_name: api
    build:
      context: ./api
      dockerfile: Dockerfile-dev
    ports:
      - "4001:80"
    volumes:
      - ./api/src:/usr/src/app/src:z
      - /tmp/api/npm-cache:/root/.npm:z
    environment:
      - PORT=80
      - NODE_ENV=development
      - DATABASE_URL=postgresql://dev:devpass@db:5432/myapp
    depends_on:
      - db
    restart: "no"

  # External Services
  db:
    image: postgres:15
    container_name: db
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=dev
      - POSTGRES_PASSWORD=devpass
      - POSTGRES_DB=myapp
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  postgres-data:
```
