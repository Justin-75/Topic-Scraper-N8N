# Transcript bridge: runs transcript_server.py, which calls YoutubeTranscript.py once per request.
# n8n itself is not built here; docker-compose.yml pulls the official n8n image.
ARG PYTHON_IMAGE=python:3.12-slim
FROM ${PYTHON_IMAGE}

ARG PIP_INDEX_URL=https://pypi.org/simple

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --index-url "${PIP_INDEX_URL}" -r requirements.txt
COPY YoutubeTranscript.py transcript_server.py ./

# Without this the "listening on ..." line stays in a buffer and never reaches `docker compose logs`.
ENV PYTHONUNBUFFERED=1
EXPOSE 8765
USER nobody

# 0.0.0.0 so the n8n container can reach it; the port is not published to your computer.
CMD ["python", "transcript_server.py", "0.0.0.0"]
