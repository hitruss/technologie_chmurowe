FROM python:3.11-slim

RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY ../backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ../backend/app.py .

COPY ../frontend/index.html /usr/share/nginx/html/index.html
COPY nginx.conf /etc/nginx/nginx.conf

COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 80
CMD ["/start.sh"]
