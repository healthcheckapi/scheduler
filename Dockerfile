FROM python:3.10
EXPOSE 5000
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
CMD ["python3", "api.py"]