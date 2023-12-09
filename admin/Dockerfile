FROM python:3.10.8

COPY requirements.txt /tmp/requirements.txt
COPY . .

RUN pip install --no-cache-dir -r /tmp/requirements.txt

CMD ["uvicorn", "main:app", "--port", "8000", "--host", "0.0.0.0"]