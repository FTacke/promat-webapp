FROM python:3.12-slim

WORKDIR /app

COPY app/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY app/ ./
COPY content/ ./content/
RUN mkdir -p scripts/research_data_intake
COPY scripts/research_data_intake/apply_prod_db_payload.py ./scripts/research_data_intake/apply_prod_db_payload.py

ENV FLASK_ENV=production
EXPOSE 5000

CMD ["gunicorn", "-c", "gunicorn.conf.py", "src.app.main:app"]
