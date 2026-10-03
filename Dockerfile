FROM python:3.12-slim
WORKDIR /srv/nogain
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV NOGAIN_HOME=/srv/nogain/data/home
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
