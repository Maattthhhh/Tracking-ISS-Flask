FROM python:3.10.8

ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt \ && pip install gunicorn \ && gunicorn --version

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "manage:app"]