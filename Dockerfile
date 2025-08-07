FROM python:3.10-slim

WORKDIR /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Ensure subfolders exist inside the mounted volume path
RUN mkdir -p /data/instance /data/uploads

# Mount single volume at /data
VOLUME ["/data"]

EXPOSE 5000

CMD ["python", "run.py"]
