# syntax=docker/dockerfile:1

### Stage 1: install dependencies
FROM python:3.13-slim AS builder

# prevent Python buffering logs
ENV PYTHONUNBUFFERED=1

# install build tools & deps, clean cache, upgrade pip
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc libgl1-mesa-glx \
 && rm -rf /var/lib/apt/lists/* \
 && pip install --upgrade pip

# copy requirements and install into a venv
WORKDIR /install
COPY requirements.txt .
RUN python -m venv /opt/venv \
    && . /opt/venv/bin/activate \
    && pip install --no-cache-dir -r requirements.txt

### Stage 2: build final image
FROM python:3.13-slim

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# copy the venv from builder
COPY --from=builder /opt/venv /opt/venv

# copy application code
WORKDIR /app
COPY . .

# expose port and default env-file location
EXPOSE 8000
ENV ENV_FILE=/app/.env

# uvicorn entrypoint
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]