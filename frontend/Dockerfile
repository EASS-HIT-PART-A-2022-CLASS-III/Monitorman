FROM python:latest

WORKDIR /code

# 
COPY ./backend/requirements.txt /code/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip install streamlit
# 
COPY ./frontend /code/frontend
COPY ./shared /code/shared
# 
CMD ["streamlit", "run","frontend/main.py","--server.port", "80"]