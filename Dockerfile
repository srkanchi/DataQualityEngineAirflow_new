FROM python:3.7
RUN apt-get update && apt-get upgrade -y
WORKDIR /
COPY . .
# RUN pip install --no-cache-dir -r requirements.
RUN apt-get install libpq-dev python-dev -y && pip install psycopg2
RUN set -ex && pip install --no-cache-dir -r dqe-python/requirements.txt

CMD ["python3", "dqe-python/run_dqe_consumer.py" ]