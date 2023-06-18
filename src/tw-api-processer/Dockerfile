FROM python:3.10

COPY tw-api-processer/ tw-api-processer
RUN pip install -r tw-api-processer/requirements.txt

COPY configuration/ .
RUN pip install .

CMD ["python", "-m", "tw-api-processer"]

