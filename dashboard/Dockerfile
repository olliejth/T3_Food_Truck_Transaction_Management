FROM python:latest

# Copies txt file containing env package requirements
COPY requirements.txt .

# Pip installs required packages.
RUN pip install -r requirements.txt

# Copies working files.
COPY functions.py .
COPY dashboard_app.py .

# Runs pipeline
CMD ["streamlit", "run", "dashboard_app.py"]