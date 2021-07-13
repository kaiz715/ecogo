FROM python:3.8-slim
WORKDIR /src
ENV PYTHONUNBUFFERED=1
#ENV FLASK_APP=app.py
#ENV FLASK_RUN_HOST=0.0.0.0
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
USER www-data
CMD ["gunicorn", "--bind=0.0.0.0:5000", "app:app"]
