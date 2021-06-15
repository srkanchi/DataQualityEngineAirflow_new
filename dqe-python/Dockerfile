FROM python:3.7
RUN apt-get update
WORKDIR /
COPY . .
# RUN pip install --no-cache-dir -r requirements.txt
RUN set -ex && pip install --no-cache-dir -r requirements.txt

CMD ["python3", "run_dqe_consumer.py" ]