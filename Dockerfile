#-----------frontend stage-------------
FROM node:20-alpine AS frontend
WORKDIR /app/

RUN npm install -g npm@11.6.1
COPY frontend/package.json frontend/package-lock.json ./frontend/
#npm ci = clean install
RUN cd frontend && npm ci

COPY frontend/src ./frontend/src
COPY frontend/public ./frontend/public
RUN cd frontend && npm run build


#-----------backend builder------------
FROM python:3.13-slim AS backend-builder
WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PROJ_LIB=/usr/share/proj

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libgeos-dev \
 && rm -rf /var/lib/apt/lists/*

    
COPY backend/pixi.toml ./
COPY backend/pixi.lock ./


# Install Poetry
RUN curl -fsSL https://pixi.sh/install.sh | sh \
    && /root/.pixi/bin/pixi install \
    && rm -rf /root/.cache/pip /root/.cache/pixi


# Copy app code
COPY backend ./backend


#-----------backend runtime------------
FROM python:3.13-slim AS backend
WORKDIR /app

ENV PATH="/app/.pixi/envs/default/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PROJ_LIB=/usr/share/proj
    
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libgeos-dev curl \
 && rm -rf /var/lib/apt/lists/*

# Copy Python libs and backend code from builder
COPY --from=backend-builder /app/.pixi/envs /app/.pixi/envs
COPY --from=backend-builder /app/backend ./backend
COPY --from=frontend /app/frontend/build ./frontend/build

EXPOSE 5000
CMD ["python", "-m", "uvicorn", "backend.run:app", "--host", "0.0.0.0", "--port", "5000"]