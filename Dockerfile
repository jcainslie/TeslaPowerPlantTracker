FROM python:3.10-slim

WORKDIR /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Ensure folders exist
RUN mkdir -p /app/instance /app/uploads

# Declare volumes for persistence
VOLUME ["/app/instance", "/app/uploads"]

EXPOSE 5000

CMD ["python", "run.py"]
