# Stage 1: Build frontend
FROM node:20-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python API + static frontend
FROM python:3.11-slim
WORKDIR /app

# Install poppler-utils (required by pdf2image)
RUN apt-get update && \
    apt-get install -y --no-install-recommends poppler-utils && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY takeoff_system/ ./takeoff_system/
COPY api/ ./api/

# Copy built frontend
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

EXPOSE 10000

CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "10000"]
