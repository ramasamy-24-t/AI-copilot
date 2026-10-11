FROM python:3.11-slim AS base
WORKDIR /app
COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY backend /app/backend
ENV PYTHONPATH=/app/backend
RUN useradd --uid 10001 --create-home health && mkdir -p /data/storage && chown -R health:health /data
# Start as root so Railway volume mounts can be chowned, then drop to health.
USER root
EXPOSE 8000
CMD ["python", "/app/backend/entrypoint.py"]
