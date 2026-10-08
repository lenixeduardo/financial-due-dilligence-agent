FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY backend/app /app/app
COPY backend/scripts /app/scripts
RUN groupadd --gid 10001 finsight && useradd --uid 10001 --gid 10001 --create-home finsight
USER 10001:10001
EXPOSE 8000
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000","--proxy-headers","--forwarded-allow-ips","*"]
