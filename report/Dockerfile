FROM public.ecr.aws/lambda/python:latest

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY html_writer.py .
COPY lambda_handler.py .
COPY report.py .
COPY report_functions.py .

CMD [ "lambda_handler.handler" ]
