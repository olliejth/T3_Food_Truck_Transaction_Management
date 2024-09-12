# Specifies latest image of python
FROM python:latest

# Copies txt file containing env package requirements
COPY requirements.txt .

# Pip installs required packages.
RUN pip install -r requirements.txt
RUN mkdir data

# Copies working files.
COPY pipeline.py .
COPY extract.py .
COPY transform.py .
COPY load.py .

# Runs pipeline
CMD ["python", "pipeline.py"]

