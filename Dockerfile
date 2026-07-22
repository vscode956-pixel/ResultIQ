# --- Stage 1: Build React Frontend ---
FROM node:20-alpine AS frontend-builder
WORKDIR /app/client
COPY client/package*.json ./
RUN npm ci
COPY client/ ./
RUN npm run build

# --- Stage 2: Build Flask Backend & Package App ---
FROM python:3.12-slim
WORKDIR /app

# Install standard dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend files
COPY . .

# Copy built frontend assets from Stage 1
COPY --from=frontend-builder /app/client/dist /app/client/dist

EXPOSE 5000

ENV PORT=5000
ENV FLASK_ENV=production

CMD ["python", "server.py"]

