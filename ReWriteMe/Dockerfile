## Multi‑stage build for ReWriteMe

# Stage 1: Build frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
# Copy package definition and install dependencies
COPY frontend/package.json ./
RUN npm install --silent
COPY frontend/ .
RUN npm run build

# Stage 2: Build backend
FROM python:3.10-slim AS backend-builder
WORKDIR /app
# Copy backend source and install dependencies
COPY backend/ ./backend
RUN pip install --no-cache-dir -r backend/requirements.txt

# Stage 3: Final runtime image
FROM python:3.10-slim
WORKDIR /app

# Copy backend code and dependencies
COPY --from=backend-builder /app/backend ./backend
# Copy prebuilt frontend assets into backend static directory
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]