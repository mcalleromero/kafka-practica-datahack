FROM python:3.10

COPY tw-api/ tw-api
RUN pip install -r tw-api/requirements.txt

COPY configuration/ .
RUN pip install .


CMD ["uvicorn", "tw-api.twitter.__main__:app", "--host", "0.0.0.0", "--port", "8099"]