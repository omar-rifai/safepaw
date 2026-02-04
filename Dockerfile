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
FROM python:3.13-alpine AS backend-builder
WORKDIR /app

ENV PATH="/root/.local/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    PROJ_LIB=/usr/share/proj

# Build deps ONLY in builder
RUN apk add --no-cache \
    build-base linux-headers musl-dev \
    curl \
    proj proj-dev \
    gdal gdal-dev \
    geos geos-dev

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

COPY backend/pyproject.toml ./
RUN poetry install --no-root --only main && rm -rf /root/.cache/pip /root/.cache/pypoetry

# Copy app code
COPY backend ./backend


#-----------backend runtime------------
FROM python:3.13-alpine AS backend
WORKDIR /app

ENV PATH="/root/.local/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    PROJ_LIB=/usr/share/proj 


RUN apk add --no-cache \
    proj \
    gdal \
    geos \
    libstdc++ \
    curl

# Copy Python libs from builder ( bit tricky but we avoid all the building stuff that are useless)
COPY --from=backend-builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin


# Copy backend and frontend
COPY --from=backend-builder /app/backend ./backend
COPY --from=frontend /app/frontend/build ./frontend/build

EXPOSE 5000
CMD ["python", "-m", "uvicorn", "backend.run:app", "--host", "0.0.0.0", "--port", "5000"]
