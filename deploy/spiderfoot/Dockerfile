# Optional SpiderFoot sidecar — passive OSINT modules only by default in OSINTGraph plugin.
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    gcc \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN git clone --depth 1 --branch v4.0 https://github.com/smicallef/spiderfoot.git . \
    && pip install --no-cache-dir -r requirements.txt

EXPOSE 5001

VOLUME ["/var/lib/spiderfoot"]

CMD ["python3", "sf.py", "-l", "0.0.0.0:5001"]
