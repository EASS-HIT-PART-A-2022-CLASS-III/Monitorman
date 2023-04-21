FROM python:latest

WORKDIR /code

# 
COPY ./backend/requirements.txt /code/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip install uvicorn
# 
COPY ./backend /code/backend
COPY ./shared /code/shared
# 
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "80"]