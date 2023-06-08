FROM python:3.10

COPY predictor/ predictor
RUN pip install -r predictor/requirements.txt

COPY configuration/ .
RUN pip install .

CMD ["python", "-m", "predictor"]

