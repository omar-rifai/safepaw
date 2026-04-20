#-----------frontend stage-------------
FROM node:20-alpine AS frontend
WORKDIR /app/

#RUN npm install -g npm@11.6.1
COPY frontend/package.json frontend/package-lock.json ./frontend/
RUN cd frontend && npm ci

COPY frontend/src ./frontend/src
COPY frontend/public ./frontend/public
RUN cd frontend && npm run build


#-----------backend ------------
FROM python:3.13-slim AS backend
WORKDIR /app

ENV PATH="/root/.pixi/bin:/app/.pixi/envs/default/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PROJ_LIB=/usr/share/proj
    
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libgeos-dev curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://pixi.sh/install.sh | sh

COPY backend/pixi.toml backend/pixi.lock ./
RUN /root/.pixi/bin/pixi install --locked \
    && rm -rf /root/.cache/rattler \
    && rm -rf /tmp/*


# Copy Python libs and backend code from builder
COPY backend ./backend
COPY --from=frontend /app/frontend/build ./frontend/build

EXPOSE 5000
CMD ["pixi", "run", "-m","backend", "python", "-m", "uvicorn", "backend.run:app", "--host", "0.0.0.0", "--port", "5000"]