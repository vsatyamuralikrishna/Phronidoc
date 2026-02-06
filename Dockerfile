# Multi-stage build for Phronidoc Editor Service

# Stage 1: Backend
FROM python:3.11-slim as backend

WORKDIR /app/backend

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY editor-service/backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY editor-service/backend/ .

# Stage 2: Frontend (static files)
FROM nginx:alpine as frontend

# Copy frontend files
COPY editor-service/frontend/ /usr/share/nginx/html/

# Stage 3: Final combined image
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY editor-service/backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy backend from stage 1
COPY --from=backend /app/backend /app/backend

# Copy frontend from stage 2
COPY --from=frontend /usr/share/nginx/html /app/frontend

# Copy nginx configuration
COPY editor-service/nginx.conf /etc/nginx/conf.d/default.conf

# Create startup script
RUN echo '#!/bin/bash\n\
# Start nginx in background\n\
nginx\n\
# Start backend\n\
cd /app/backend && python main.py\n\
' > /app/start.sh && chmod +x /app/start.sh

EXPOSE 80 8001

CMD ["/app/start.sh"]
