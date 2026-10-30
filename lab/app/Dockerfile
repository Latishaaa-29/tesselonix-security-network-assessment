FROM python:3.11-slim
WORKDIR /srv/microblog
COPY app/microblog/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt pytest==8.3.5
COPY app/microblog/ .
COPY lab/app/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENV FLASK_APP=microblog.py LOG_TO_STDOUT=1 PYTHONUNBUFFERED=1
EXPOSE 5000
ENTRYPOINT ["/entrypoint.sh"]
