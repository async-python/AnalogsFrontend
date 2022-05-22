FROM python:3.10-slim-buster
WORKDIR /flask
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY . .
EXPOSE 5000
CMD ["gunicorn","-w", "4", "-b", "0.0.0.0:5000", "app:create_app()"]