# Docker Setup

You can easily setup the Database and other Services using these Docker Images:

- [Database Image](https://github.com/open-discourse/open-discourse/pkgs/container/open-discourse%2Fdatabase)
- [Proxy Image](https://github.com/open-discourse/open-discourse/pkgs/container/open-discourse%2Fproxy)
- [Frontend Image](https://github.com/open-discourse/open-discourse/pkgs/container/open-discourse%2Ffrontend)

To connect all of the Images, you can use `docker-compose`.

Sample `docker-compose.yml`:

```yaml
services:
  database:
    container_name: od-database
    image: docker.pkg.github.com/open-discourse/open-discourse/database:latest
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 5
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_DB=postgres
      - POSTGRES_PASSWORD=postgres

  proxy:
    container_name: od-proxy
    image: docker.pkg.github.com/open-discourse/open-discourse/proxy:latest
    depends_on:
      database:
        condition: service_healthy
    environment:
      - POSTGRES_DB_HOST=database
      - CACHE_EXPIRATION=100000
      - QUERY_LIMIT=500
    ports:
      - "5300:5300"

  frontend:
    container_name: od-frontend
    image: docker.pkg.github.com/open-discourse/open-discourse/frontend:latest
    depends_on:
      proxy:
        condition: service_started
    environment:
      - PROXY_ENDPOINT=http://localhost:5300
    ports:
      - "80:80"
```
