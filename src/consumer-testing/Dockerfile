FROM python:3.10

COPY consumer-testing/ consumer-testing
RUN pip install -r consumer-testing/requirements.txt

COPY configuration/ .
RUN pip install .

CMD ["python", "-m", "consumer-testing"]

