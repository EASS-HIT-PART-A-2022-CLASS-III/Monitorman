FROM python:latest

WORKDIR /code

# 
COPY ./scheduler/requirements.txt /code/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip install uvicorn
# 
COPY ./scheduler /code/scheduler
COPY ./shared /code/shared
# 
CMD ["uvicorn", "scheduler.main:app", "--host", "0.0.0.0", "--port", "80"]