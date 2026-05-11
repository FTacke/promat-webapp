FROM python:3.12-slim

WORKDIR /app

COPY app/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY app/ ./
COPY content/ ./content/

ENV FLASK_ENV=production
EXPOSE 5000

CMD ["python", "-m", "src.app.main"]